import React, { useState, useMemo } from 'react';
import PropTypes from 'prop-types';
import { Calendar, Building2, Gavel, FileText, ChevronDown, ChevronUp, Search, X, FileJson, Download } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { getPhaseColorClasses, getPhaseDisplayName } from '../utils/phaseColors';
import { normalizePhaseWithMovements } from '../constants/phases';
import InstanceSelector from './InstanceSelector';

function ProcessDetails({ data }) {
    const [showAll, setShowAll] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedDocTypes, setSelectedDocTypes] = useState([]); // Empty array means 'Todos'

    const [showJson, setShowJson] = useState(false);

    const DOC_TYPES = useMemo(() => ({
        'Decisões': ['3', '193', '246', '80', '81'],
        'Petições': ['11011', '85', '60', '50', '7', '67', '66', '56', '59'],
        'Despachos': ['11010', '11009'],
        'Citações': ['122', '123', '124', '15216', '12177']
    }), []);

    // Calculate distribution date from the earliest movement
    const distributionDate = useMemo(() => {
        if (!data?.movements?.length) return data?.distribution_date;
        const sorted = [...data.movements].sort((a, b) => new Date(a.date) - new Date(b.date));
        return sorted[0].date;
    }, [data?.movements, data?.distribution_date]);

    // Corrigir fase considerando movimentos (força Fase 15 se houver baixa)
    const correctedPhase = useMemo(() => {
        return normalizePhaseWithMovements(data?.phase, data?.class_nature, data?.movements);
    }, [data?.phase, data?.class_nature, data?.movements]);

    const filteredMovements = useMemo(() => {
        if (!data?.movements) return [];

        let filtered = data.movements;

        // Apply Document Type Filter (Multi-select OR logic)
        if (selectedDocTypes.length > 0) {
            filtered = filtered.filter(mov => {
                const sCode = String(mov.code);
                return selectedDocTypes.some(type => DOC_TYPES[type]?.includes(sCode));
            });
        }

        // Apply Text Search Filter
        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            filtered = filtered.filter(mov =>
                (mov.description || '').toLowerCase().includes(term) ||
                (mov.code || '').toLowerCase().includes(term)
            );
        }

        return filtered;
    }, [data?.movements, searchTerm, selectedDocTypes, DOC_TYPES]);

    const toggleFilter = (type) => {
        if (type === 'Todos') {
            setSelectedDocTypes([]);
            return;
        }

        setSelectedDocTypes(prev => {
            if (prev.includes(type)) {
                return prev.filter(t => t !== type);
            } else {
                return [...prev, type];
            }
        });
        setShowAll(false);
    };

    const handleDownloadJson = () => {
        if (!data.raw_data) return;
        const jsonString = JSON.stringify(data.raw_data, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `processo-${data.number}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    const getCategoryStyles = (category) => {
        switch (category) {
            case 'Decisões': return 'bg-amber-100 text-amber-700 border-amber-200';
            case 'Petições': return 'bg-sky-100 text-sky-700 border-sky-200';
            case 'Despachos': return 'bg-emerald-100 text-emerald-700 border-emerald-200';
            case 'Citações': return 'bg-purple-100 text-purple-700 border-purple-200';
            default: return 'bg-gray-100 text-gray-600 border-gray-200';
        }
    };

    const getMovementCategory = (code) => {
        const sCode = String(code);
        if (DOC_TYPES['Decisões'].includes(sCode)) return 'Decisões';
        if (DOC_TYPES['Petições'].includes(sCode)) return 'Petições';
        if (DOC_TYPES['Despachos'].includes(sCode)) return 'Despachos';
        if (DOC_TYPES['Citações'].includes(sCode)) return 'Citações';
        return null;
    };

    if (!data) return null;

    const displayedMovements = showAll ? filteredMovements : filteredMovements.slice(0, 20);
    const hasMore = filteredMovements.length > 20;

    return (
        <article className="max-w-4xl mx-auto p-4 space-y-6" aria-labelledby="process-title">
            {/* Instance Selector - Shows when multiple instances exist */}
            <InstanceSelector processNumber={data.number} meta={data?.raw_data?.__meta__} />

            {/* Header Card */}
            <section className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden" aria-label="Informações do processo">
                <header className="bg-gradient-to-r from-indigo-600 to-violet-600 p-6 text-white flex justify-between items-start">
                    <div>
                        <h1 id="process-title" className="text-2xl font-bold font-mono tracking-wide">{data.number}</h1>
                        <p className="opacity-90 mt-1">{data.subject || 'Assunto não informado'}</p>
                    </div>
                    {data.raw_data && (
                        <div className="flex space-x-2">
                            <button
                                onClick={() => setShowJson(!showJson)}
                                className="p-2 bg-white/20 hover:bg-white/30 rounded-lg text-white transition-colors"
                                title="Ver JSON Bruto"
                            >
                                <FileJson className="h-5 w-5" />
                            </button>
                            <button
                                onClick={handleDownloadJson}
                                className="p-2 bg-white/20 hover:bg-white/30 rounded-lg text-white transition-colors"
                                title="Baixar JSON"
                            >
                                <Download className="h-5 w-5" />
                            </button>
                        </div>
                    )}
                </header>
                <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
                    <div className="flex items-start space-x-3">
                        <Gavel className="h-5 w-5 text-indigo-500 mt-1" />
                        <div>
                            <p className="text-xs text-gray-500 uppercase font-semibold">Classe</p>
                            <p className="text-sm font-medium text-gray-900 leading-tight">{data.class_nature || 'N/A'}</p>
                        </div>
                    </div>
                    <div className="flex items-start space-x-3">
                        <Building2 className="h-5 w-5 text-indigo-500 mt-1" />
                        <div>
                            <p className="text-xs text-gray-500 uppercase font-semibold">Tribunal / Vara</p>
                            <p className="text-sm font-medium text-gray-900 leading-tight">{data.court || 'N/A'}</p>
                        </div>
                    </div>
                    <div className="flex items-start space-x-3">
                        <Calendar className="h-5 w-5 text-indigo-500 mt-1" />
                        <div>
                            <p className="text-xs text-gray-500 uppercase font-semibold">Distribuição</p>
                            <p className="text-sm font-medium text-gray-900">
                                {distributionDate
                                    ? format(new Date(distributionDate), "dd/MM/yyyy", { locale: ptBR })
                                    : 'N/A'}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-start space-x-3">
                        <FileText className="h-5 w-5 text-violet-500 mt-1" aria-hidden="true" />
                        <div>
                            <p className="text-xs text-gray-500 uppercase font-semibold">Fase Atual</p>
                            <div className="mt-1">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPhaseColorClasses(correctedPhase, data.class_nature)}`}>
                                    {correctedPhase}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Timeline */}
            <section className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6" aria-labelledby="movements-heading">
                <div className="flex flex-col space-y-4 mb-6">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <h2 id="movements-heading" className="text-lg font-bold text-gray-900 flex items-center mb-0">
                            <FileText className="mr-2 h-5 w-5 text-indigo-600" aria-hidden="true" />
                            Movimentações
                            <span className="ml-2 px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-xs font-bold">
                                {filteredMovements.length}
                            </span>
                        </h2>

                        {/* Filter Input */}
                        <div className="relative max-w-sm w-full">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Search className="h-4 w-4 text-gray-400" />
                            </div>
                            <input
                                type="text"
                                placeholder="Buscar no texto..."
                                className="block w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg text-sm focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                            {searchTerm && (
                                <button
                                    onClick={() => setSearchTerm('')}
                                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                                >
                                    <X className="h-4 w-4" />
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Document Type Chips (Multi-select) */}
                    <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-50">
                        <button
                            onClick={() => toggleFilter('Todos')}
                            className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all border shadow-sm ${selectedDocTypes.length === 0
                                ? 'bg-indigo-600 text-white border-indigo-600'
                                : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300 hover:text-indigo-600'
                                }`}
                        >
                            Todos
                        </button>
                        {Object.keys(DOC_TYPES).map(type => {
                            const isActive = selectedDocTypes.includes(type);
                            return (
                                <button
                                    key={type}
                                    onClick={() => toggleFilter(type)}
                                    className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all border shadow-sm ${isActive
                                        ? 'bg-indigo-600 text-white border-indigo-600'
                                        : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300 hover:text-indigo-600'
                                        }`}
                                >
                                    {type}
                                </button>
                            );
                        })}
                    </div>
                </div>

                <ol className="relative border-l-2 border-indigo-100 ml-3 space-y-8 pl-8 pb-4 list-none">
                    {displayedMovements.map((mov, idx) => {
                        const category = getMovementCategory(mov.code);
                        return (
                            <li key={mov.id || idx} className="relative animate-in fade-in slide-in-from-left-4 duration-300">
                                <span className="absolute -left-[41px] top-1 h-5 w-5 rounded-full border-4 border-white bg-indigo-500 shadow-sm" aria-hidden="true" />
                                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start">
                                    <div className="flex-1 pr-4">
                                        <div className="flex items-center flex-wrap gap-2 mb-1">
                                            <p className="text-base font-medium text-gray-900">{mov.description}</p>
                                            {category && (
                                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${getCategoryStyles(category)}`}>
                                                    {category}
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-sm text-gray-500 mt-1 uppercase tracking-tight font-semibold">Código: {mov.code || 'S/N'}</p>
                                    </div>
                                    <time
                                        dateTime={mov.date}
                                        className="text-xs font-mono text-gray-400 whitespace-nowrap bg-gray-50 px-2 py-1 rounded mt-2 sm:mt-0 font-bold"
                                    >
                                        {format(new Date(mov.date), "dd MMM yyyy, HH:mm", { locale: ptBR })}
                                    </time>
                                </div>
                            </li>
                        );
                    })}
                    {filteredMovements.length === 0 && (
                        <li className="text-gray-500 italic py-8 text-center bg-gray-50 rounded-xl border border-dashed border-gray-200">
                            Nenhuma movimentação encontrada para os filtros selecionados.
                        </li>
                    )}
                </ol>

                {/* Show More Button */}
                {hasMore && (
                    <div className="mt-8 flex justify-center">
                        <button
                            onClick={() => setShowAll(!showAll)}
                            className="flex items-center space-x-2 px-6 py-2.5 bg-indigo-50 text-indigo-700 rounded-full font-bold text-sm hover:bg-indigo-100 transition-all border border-indigo-100 shadow-sm"
                        >
                            {showAll ? (
                                <>
                                    <ChevronUp className="h-4 w-4" />
                                    <span>Recolher movimentações</span>
                                </>
                            ) : (
                                <>
                                    <ChevronDown className="h-4 w-4" />
                                    <span>Ver mais {filteredMovements.length - 20} movimentos</span>
                                </>
                            )}
                        </button>
                    </div>
                )}
            </section>

            {/* JSON Modal */}
            {showJson && data.raw_data && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
                        <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gray-50">
                            <h3 className="text-lg font-bold text-gray-900 flex items-center">
                                <FileJson className="mr-2 h-5 w-5 text-indigo-600" />
                                Dados Brutos (DataJud)
                            </h3>
                            <div className="flex items-center space-x-2">
                                <button
                                    onClick={handleDownloadJson}
                                    className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-bold hover:bg-indigo-700 transition-colors"
                                >
                                    <Download className="mr-2 h-4 w-4" />
                                    Baixar JSON
                                </button>
                                <button
                                    onClick={() => setShowJson(false)}
                                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                                >
                                    <X className="h-5 w-5" />
                                </button>
                            </div>
                        </div>
                        <div className="flex-1 overflow-auto p-6 bg-gray-900">
                            <pre className="font-mono text-sm text-green-400 overflow-x-auto">
                                <code>{JSON.stringify(data.raw_data, null, 2)}</code>
                            </pre>
                        </div>
                    </div>
                </div>
            )}
        </article>
    );
}

ProcessDetails.propTypes = {
    data: PropTypes.shape({
        number: PropTypes.string.isRequired,
        subject: PropTypes.string,
        class_nature: PropTypes.string,
        court: PropTypes.string,
        distribution_date: PropTypes.string,
        phase: PropTypes.string,
        movements: PropTypes.arrayOf(
            PropTypes.shape({
                id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
                description: PropTypes.string.isRequired,
                code: PropTypes.string,
                date: PropTypes.string.isRequired,
            })
        ),
    }),
};

export default ProcessDetails;
