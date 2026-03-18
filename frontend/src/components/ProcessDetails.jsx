import React, { useState, useMemo, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { LoadingState, ErrorState } from './LoadingState';
import { Calendar, Building2, Gavel, FileText, ChevronDown, ChevronUp, Search, X, FileJson, Download, RefreshCw, ArrowDownUp, Database, Pencil } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { getPhaseColorClasses } from '../utils/phaseColors';
import { normalizePhaseWithMovements, PHASE_BY_CODE } from '../constants/phases';
import InstanceSelector from './InstanceSelector';
import { getProcessInstance } from '../services/api';
import { toast } from 'react-hot-toast';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import PhaseEditModal from './PhaseEditModal';

function ProcessDetails({ data }) {
    const [activeData, setActiveData] = useState(data);
    const [loadingInstance, setLoadingInstance] = useState(false);
    const [showJson, setShowJson] = useState(false);
    const jsonDialogRef = useRef(null);

    // Sync local state when props change
    useEffect(() => {
        setActiveData(data);
    }, [data]);

    // ESC key closes JSON modal — REM-029
    useEffect(() => {
        if (!showJson) return;
        const handleEsc = (e) => {
            if (e.key === 'Escape') setShowJson(false);
        };
        document.addEventListener('keydown', handleEsc);
        return () => document.removeEventListener('keydown', handleEsc);
    }, [showJson]);

    // Focus trap for JSON modal — REM-029
    useEffect(() => {
        if (!showJson || !jsonDialogRef.current) return;

        const focusable = jsonDialogRef.current.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstEl = focusable[0];
        const lastEl = focusable[focusable.length - 1];

        if (firstEl) firstEl.focus();

        const handleTab = (e) => {
            if (e.key !== 'Tab') return;
            if (focusable.length === 0) { e.preventDefault(); return; }

            if (e.shiftKey) {
                if (document.activeElement === firstEl) {
                    e.preventDefault();
                    lastEl.focus();
                }
            } else {
                if (document.activeElement === lastEl) {
                    e.preventDefault();
                    firstEl.focus();
                }
            }
        };

        document.addEventListener('keydown', handleTab);
        return () => document.removeEventListener('keydown', handleTab);
    }, [showJson]);

    const [showAll, setShowAll] = useState(false);
    const [showAllFusion, setShowAllFusion] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedDocTypes, setSelectedDocTypes] = useState([]); // Empty array means 'Todos'
    const [movSort, setMovSort] = useState('desc');       // 'desc' | 'asc' — movimentações DataJud
    const [fusionSort, setFusionSort] = useState('desc'); // 'desc' | 'asc' — movimentações Fusion
    const [manualPhase, setManualPhase] = useState(null);  // Fase corrigida manualmente
    const [showPhaseEdit, setShowPhaseEdit] = useState(false); // Modal de edição de fase

    const DOC_TYPES = useMemo(() => ({
        'Decisões': ['3', '193', '246', '80', '81'],
        'Petições': ['11011', '85', '60', '50', '7', '67', '66', '56', '59'],
        'Despachos': ['11010', '11009'],
        'Citações': ['122', '123', '124', '15216', '12177']
    }), []);

    // Calculate distribution date from the earliest movement
    const distributionDate = useMemo(() => {
        if (!activeData?.movements?.length) return activeData?.distribution_date;
        const sorted = [...activeData.movements].sort((a, b) => new Date(a.date) - new Date(b.date));
        return sorted[0].date;
    }, [activeData?.movements, activeData?.distribution_date]);

    // Corrigir fase considerando movimentos (força Fase 15 se houver baixa)
    // Prioriza manualPhase se foi corrigida manualmente
    const correctedPhase = useMemo(() => {
        if (manualPhase) {
            // Se foi corrigida manualmente, usar a nova fase
            return PHASE_BY_CODE[manualPhase]?.name || manualPhase;
        }
        return normalizePhaseWithMovements(activeData?.phase, activeData?.class_nature, activeData?.movements);
    }, [manualPhase, activeData?.phase, activeData?.class_nature, activeData?.movements]);

    const filteredMovements = useMemo(() => {
        if (!activeData?.movements) return [];

        let filtered = activeData.movements;

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

        // Apply sort
        return [...filtered].sort((a, b) => {
            const diff = new Date(a.date) - new Date(b.date);
            return movSort === 'desc' ? -diff : diff;
        });
    }, [activeData?.movements, searchTerm, selectedDocTypes, DOC_TYPES, movSort]);

    const fusionMovements = useMemo(() => {
        const movs = activeData?.fusion_movements;
        if (!movs?.length) return [];
        return [...movs].sort((a, b) => {
            const diff = new Date(a.date) - new Date(b.date);
            return fusionSort === 'desc' ? -diff : diff;
        });
    }, [activeData?.fusion_movements, fusionSort]);

    const displayedFusionMovements = showAllFusion ? fusionMovements : fusionMovements.slice(0, 20);
    const hasFusionMore = fusionMovements.length > 20;

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

    const handleInstanceChange = async (instanceMeta) => {
        if (!instanceMeta || typeof instanceMeta.index === 'undefined') return;

        setLoadingInstance(true);
        try {
            const newInstanceData = await getProcessInstance(activeData.number, instanceMeta.index);
            setActiveData(newInstanceData);
            toast.success(`Visualizando ${instanceMeta.grau_label || instanceMeta.grau || 'Instância selecionada'}`);
        } catch (error) {
            console.error("Erro ao trocar instância:", error);
            toast.error("Erro ao carregar instância");
        } finally {
            setLoadingInstance(false);
        }
    };

    const handleDownloadJson = () => {
        if (!activeData.raw_data) return;
        const jsonString = JSON.stringify(activeData.raw_data, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `processo-${activeData.number}.json`;
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

    if (!activeData) return null;

    const displayedMovements = showAll ? filteredMovements : filteredMovements.slice(0, 20);
    const hasMore = filteredMovements.length > 20;

    return (
        <article className={`max-w-4xl mx-auto p-4 space-y-6 ${loadingInstance ? 'opacity-50 pointer-events-none' : ''}`} aria-labelledby="process-title">
            {loadingInstance && (
                <div
                    role="status"
                    aria-label="Carregando instância do processo"
                    className="fixed inset-0 z-50 flex items-center justify-center bg-white/30 backdrop-blur-[1px]"
                >
                    <div className="bg-white p-4 rounded-full shadow-lg">
                        <RefreshCw className="h-8 w-8 text-indigo-600 animate-spin" aria-hidden="true" />
                    </div>
                </div>
            )}

            {/* Instance Selector - Shows when multiple instances exist */}
            <InstanceSelector
                key={activeData.number}
                processNumber={activeData.number}
                meta={activeData?.raw_data?.__meta__}
                onInstanceChange={handleInstanceChange}
            />

            {/* Header Card */}
            <Card className="overflow-hidden" aria-label="Informações do processo">
                <header className="bg-gradient-to-r from-indigo-600 to-violet-600 p-6 text-white flex justify-between items-start rounded-t-2xl">
                    <div>
                        <h1 id="process-title" className="text-2xl font-bold font-mono tracking-wide">{activeData.number}</h1>
                        <p className="opacity-90 mt-1">{activeData.subject || 'Assunto não informado'}</p>
                    </div>
                    {activeData.raw_data && (
                        <div className="flex space-x-2">
                            <Button
                                onClick={() => setShowJson(!showJson)}
                                variant="ghost"
                                className="p-2 bg-white/20 hover:bg-white/30 rounded-lg text-white transition-colors"
                                title="Ver JSON Bruto"
                            >
                                <FileJson className="h-5 w-5" />
                            </Button>
                            <Button
                                onClick={handleDownloadJson}
                                variant="ghost"
                                className="p-2 bg-white/20 hover:bg-white/30 rounded-lg text-white transition-colors"
                                title="Baixar JSON"
                            >
                                <Download className="h-5 w-5" />
                            </Button>
                        </div>
                    )}
                </header>
                <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
                    <div className="flex items-start space-x-3">
                        <Gavel className="h-5 w-5 text-indigo-500 mt-1" />
                        <div>
                            <p className="text-xs text-gray-500 uppercase font-semibold">Classe</p>
                            <p className="text-sm font-medium text-gray-900 leading-tight">{activeData.class_nature || 'N/A'}</p>
                        </div>
                    </div>
                    <div className="flex items-start space-x-3">
                        <Building2 className="h-5 w-5 text-indigo-500 mt-1" />
                        <div>
                            <p className="text-xs text-gray-500 uppercase font-semibold">Tribunal / Vara</p>
                            <p className="text-sm font-medium text-gray-900 leading-tight">{activeData.court || 'N/A'}</p>
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
                        <div className="flex-1">
                            <p className="text-xs text-gray-500 uppercase font-semibold">Fase Atual</p>
                            <div className="mt-1 flex items-center flex-wrap gap-1.5">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${correctedPhase === 'Indefinido' ? 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 border border-gray-300 dark:border-gray-600' : getPhaseColorClasses(correctedPhase, activeData.class_nature)}`}>
                                    {correctedPhase}
                                </span>
                                {/* Badge "Corrigida" quando manualmente editada */}
                                {manualPhase && (
                                    <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-violet-100 text-violet-800 border border-violet-300 dark:bg-violet-900/30 dark:text-violet-300 dark:border-violet-700">
                                        Corrigida
                                    </span>
                                )}
                                {/* Badge de origem da fase */}
                                {activeData.phase_source && activeData.phase_source !== 'datajud' && (
                                    <span
                                        className="px-2 py-0.5 text-xs font-medium rounded-full bg-amber-100 text-amber-800 border border-amber-300"
                                        title="Fase classificada via PAV/Fusion — processo não encontrado no DataJud"
                                    >
                                        Fusion
                                    </span>
                                )}
                                {/* Botão de edição */}
                                <button
                                    onClick={() => setShowPhaseEdit(true)}
                                    className="p-1 rounded text-gray-400 hover:text-gray-600 dark:hover:text-gray-300
                                             hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors
                                             focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                    title="Editar fase"
                                    aria-label="Editar fase processual"
                                >
                                    <Pencil className="h-4 w-4" />
                                </button>
                            </div>
                            {/* Aviso quando fase não pôde ser determinada */}
                            {activeData.phase_warning && (
                                <p className="mt-1.5 text-xs text-amber-700 dark:text-amber-400 flex items-center gap-1">
                                    <span aria-hidden="true">⚠</span>
                                    {activeData.phase_warning}
                                </p>
                            )}
                        </div>
                    </div>
                </div>
            </Card>

            {/* Movimentações Fusion — exibido apenas quando há dados do PAV */}
            {fusionMovements.length > 0 && (
                <Card className="p-0">
                <CardContent className="p-6" aria-labelledby="fusion-movements-heading">
                    <div className="flex items-center justify-between mb-5">
                        <h2 id="fusion-movements-heading" className="text-lg font-bold text-gray-900 flex items-center mb-0">
                            <Database className="mr-2 h-5 w-5 text-amber-500" aria-hidden="true" />
                            Movimentações Fusion
                            <span className="ml-2 px-2 py-0.5 bg-amber-50 text-amber-600 rounded text-xs font-bold border border-amber-200">
                                {fusionMovements.length}
                            </span>
                            <span className="ml-2 px-2 py-0.5 bg-amber-100 text-amber-700 rounded text-xs font-semibold border border-amber-200">
                                PAV
                            </span>
                        </h2>
                        <button
                            onClick={() => {
                                setFusionSort(s => s === 'desc' ? 'asc' : 'desc');
                                setShowAllFusion(false);
                            }}
                            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-amber-700 bg-amber-50 border border-amber-200 rounded-lg hover:bg-amber-100 transition-colors"
                            title={fusionSort === 'desc' ? 'Ordenado: mais recente primeiro' : 'Ordenado: mais antigo primeiro'}
                        >
                            <ArrowDownUp className="h-3.5 w-3.5" />
                            {fusionSort === 'desc' ? 'Mais recente' : 'Mais antigo'}
                        </button>
                    </div>
                    <ol className="relative border-l-2 border-amber-100 ml-3 space-y-6 pl-8 pb-2 list-none">
                        {displayedFusionMovements.map((mov, idx) => (
                            <li key={idx} className="relative">
                                <span className="absolute -left-[41px] top-1 h-5 w-5 rounded-full border-4 border-white bg-amber-400 shadow-sm" aria-hidden="true" />
                                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start">
                                    <div className="flex-1 pr-4">
                                        <p className="text-base font-medium text-gray-900">{mov.description || '—'}</p>
                                        {mov.detail && mov.detail !== mov.description && (
                                            <p className="text-sm text-gray-600 mt-0.5">
                                                <span className="font-semibold">Descrição: </span>{mov.detail}
                                            </p>
                                        )}
                                        {mov.code && mov.code.toLowerCase() !== 'indisponível' && (
                                            <p className="text-sm text-gray-500 mt-1 uppercase tracking-tight font-semibold">Tipo: {mov.code}</p>
                                        )}
                                    </div>
                                    <time
                                        dateTime={mov.date}
                                        className="text-xs font-mono text-amber-600 whitespace-nowrap bg-amber-50 px-2 py-1 rounded mt-2 sm:mt-0 font-bold"
                                    >
                                        {format(new Date(mov.date), "dd MMM yyyy, HH:mm", { locale: ptBR })}
                                    </time>
                                </div>
                            </li>
                        ))}
                    </ol>

                    {/* Show More Button for Fusion */}
                    {hasFusionMore && (
                        <div className="mt-8 flex justify-center">
                            <Button
                                onClick={() => setShowAllFusion(!showAllFusion)}
                                variant="outline"
                                className="flex items-center space-x-2 px-6 py-2.5 bg-amber-50 text-amber-700 rounded-full font-bold text-sm hover:bg-amber-100 transition-all border border-amber-100 shadow-sm"
                            >
                                {showAllFusion ? (
                                    <>
                                        <ChevronUp className="h-4 w-4" />
                                        <span>Recolher movimentações</span>
                                    </>
                                ) : (
                                    <>
                                        <ChevronDown className="h-4 w-4" />
                                        <span>Ver mais {fusionMovements.length - 20} movimentos</span>
                                    </>
                                )}
                            </Button>
                        </div>
                    )}
                </CardContent>
                </Card>
            )}

            {/* Timeline */}
            <Card className="p-0">
            <CardContent className="p-6" aria-labelledby="movements-heading">
                <div className="flex flex-col space-y-4 mb-6">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="flex items-center gap-3 flex-wrap">
                            <h2 id="movements-heading" className="text-lg font-bold text-gray-900 flex items-center mb-0">
                                <FileText className="mr-2 h-5 w-5 text-indigo-600" aria-hidden="true" />
                                Movimentações
                                <span className="ml-2 px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-xs font-bold">
                                    {filteredMovements.length}
                                </span>
                            </h2>
                            <button
                                onClick={() => setMovSort(s => s === 'desc' ? 'asc' : 'desc')}
                                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-lg hover:bg-indigo-100 transition-colors"
                                title={movSort === 'desc' ? 'Ordenado: mais recente primeiro' : 'Ordenado: mais antigo primeiro'}
                            >
                                <ArrowDownUp className="h-3.5 w-3.5" />
                                {movSort === 'desc' ? 'Mais recente' : 'Mais antigo'}
                            </button>
                        </div>

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
                        <Button
                            onClick={() => setShowAll(!showAll)}
                            variant="outline"
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
                        </Button>
                    </div>
                )}
            </CardContent>
            </Card>

            {/* JSON Modal */}
            {showJson && activeData.raw_data && (
                <div
                    className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200"
                    role="presentation"
                    onClick={(e) => { if (e.target === e.currentTarget) setShowJson(false); }}
                >
                    <div
                        ref={jsonDialogRef}
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="json-modal-title"
                        className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden"
                    >
                        <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gray-50">
                            <h3 id="json-modal-title" className="text-lg font-bold text-gray-900 flex items-center">
                                <FileJson className="mr-2 h-5 w-5 text-indigo-600" />
                                Dados Brutos (DataJud)
                            </h3>
                            <div className="flex items-center space-x-2">
                                <Button
                                    onClick={handleDownloadJson}
                                    className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-bold hover:bg-indigo-700 transition-colors"
                                >
                                    <Download className="mr-2 h-4 w-4" />
                                    Baixar JSON
                                </Button>
                                <Button
                                    onClick={() => setShowJson(false)}
                                    variant="ghost"
                                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                                >
                                    <X className="h-5 w-5" />
                                </Button>
                            </div>
                        </div>
                        <div className="flex-1 overflow-auto p-6 bg-gray-900">
                            <pre className="font-mono text-sm text-green-400 overflow-x-auto">
                                <code>{JSON.stringify(activeData.raw_data, null, 2)}</code>
                            </pre>
                        </div>
                    </div>
                </div>
            )}

            {/* Modal de Edição de Fase */}
            {showPhaseEdit && (
                <PhaseEditModal
                    processNumber={activeData.number}
                    currentPhase={correctedPhase}
                    classificationLog={activeData.raw_data?.__meta__?.classification_log}
                    sourceTab="single"
                    onClose={() => setShowPhaseEdit(false)}
                    onSuccess={(newPhaseCode) => {
                        setManualPhase(newPhaseCode);
                        toast.success('Fase corrigida com sucesso!');
                    }}
                />
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
        phase_warning: PropTypes.string,
        phase_source: PropTypes.string,
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
