import { useState, useEffect, useCallback, lazy, Suspense } from 'react';
import { Clock, Trash2, Copy, ExternalLink, FileText, CheckCircle, XCircle, AlertTriangle, ChevronDown, ChevronUp, Pencil, Check } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getHistory, clearHistory, searchProcess, confirmPhase, getConfirmedProcesses, getLatestCorrections } from '../services/api';
import { PHASE_BY_CODE, STAGES, SUBSTAGES, TRANSIT_OPTIONS } from '../constants/phases';
import { getPhaseColorClasses, getStageColorClasses } from '../utils/phaseColors';
import PhaseEditModal from './PhaseEditModal';
import ClassificationTrace from './ClassificationTrace';

const ProcessDetails = lazy(() => import('./ProcessDetails'));

const STATUS_LABELS = {
    found: { label: 'Encontrado', icon: CheckCircle, cls: 'text-green-600 bg-green-50 border-green-200' },
    not_found: { label: 'Não localizado', icon: XCircle, cls: 'text-red-600 bg-red-50 border-red-200' },
    api_error: { label: 'Erro de API', icon: AlertTriangle, cls: 'text-orange-600 bg-orange-50 border-orange-200' },
    network_error: { label: 'Erro de rede', icon: AlertTriangle, cls: 'text-orange-600 bg-orange-50 border-orange-200' },
};

const FILTERS = [
    { value: 'all', label: 'Todos' },
    { value: 'found', label: 'Encontrados' },
    { value: 'not_found', label: 'Não localizados' },
    { value: 'error', label: 'Erros' },
];

function StatusBadge({ status }) {
    const cfg = STATUS_LABELS[status] ?? STATUS_LABELS.found;
    const Icon = cfg.icon;
    return (
        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border ${cfg.cls}`}>
            <Icon className="h-3 w-3" />
            {cfg.label}
        </span>
    );
}

function PhaseBadge({ phase, corrected, onEdit, onConfirm, confirmed }) {
    if (!phase || phase === 'Indefinido') {
        return (
            <div className="flex items-center gap-1">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-500 border border-gray-200">
                    Fase Indefinida
                </span>
                {onConfirm && !corrected && (
                    <button
                        onClick={(e) => { e.stopPropagation(); onConfirm(); }}
                        disabled={confirmed}
                        className={`p-1.5 rounded-md transition-all focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-green-500 font-semibold
                            ${confirmed
                                ? 'text-white bg-green-600 border-2 border-green-700 shadow-md hover:shadow-lg cursor-default'
                                : 'text-gray-400 hover:text-green-600 hover:bg-green-50 border-2 border-transparent'}`}
                        title={confirmed ? 'Fase confirmada como correta ✓' : 'Confirmar fase como correta'}
                        aria-label="Confirmar fase como correta"
                    >
                        <Check className="h-4 w-4" />
                    </button>
                )}
                {onEdit && (
                    <button
                        onClick={(e) => { e.stopPropagation(); onEdit(); }}
                        className="p-1 rounded text-gray-400 hover:text-gray-600 dark:hover:text-gray-300
                                 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors
                                 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        title="Editar fase"
                        aria-label="Editar fase processual"
                    >
                        <Pencil className="h-3 w-3" />
                    </button>
                )}
            </div>
        );
    }
    const code = String(phase).padStart(2, '0');
    const phaseInfo = PHASE_BY_CODE[code];
    const colorCls = getPhaseColorClasses(code);
    return (
        <div className="flex items-center gap-1">
            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${colorCls}`}>
                {phaseInfo ? `${code} — ${phaseInfo.name}` : `Fase ${phase}`}
            </span>
            {corrected && (
                <span className="px-1.5 py-0.5 text-xs rounded bg-violet-100 text-violet-700 border border-violet-200">
                    Corrigida
                </span>
            )}
            {onConfirm && !corrected && (
                <button
                    onClick={(e) => { e.stopPropagation(); onConfirm(); }}
                    disabled={confirmed}
                    className={`p-1.5 rounded-md transition-all focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-green-500 font-semibold
                        ${confirmed
                            ? 'text-white bg-green-600 border-2 border-green-700 shadow-md hover:shadow-lg cursor-default'
                            : 'text-gray-400 hover:text-green-600 hover:bg-green-50 border-2 border-transparent'}`}
                    title={confirmed ? 'Fase confirmada como correta ✓' : 'Confirmar fase como correta'}
                    aria-label="Confirmar fase como correta"
                >
                    <Check className="h-4 w-4" />
                </button>
            )}
            {onEdit && (
                <button
                    onClick={(e) => { e.stopPropagation(); onEdit(); }}
                    className="p-1 rounded text-gray-400 hover:text-gray-600 dark:hover:text-gray-300
                             hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors
                             focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    title="Editar fase"
                    aria-label="Editar fase processual"
                >
                    <Pencil className="h-3 w-3" />
                </button>
            )}
        </div>
    );
}

function HistoryTab({ labels }) {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [expandedId, setExpandedId] = useState(null);
    const [phaseCorrections, setPhaseCorrections] = useState({});
    const [confirmedIds, setConfirmedIds] = useState(new Set());
    const [editingItem, setEditingItem] = useState(null);
    // Inline details state
    const [inlineDetailId, setInlineDetailId] = useState(null);
    const [inlineDetailData, setInlineDetailData] = useState(null);
    const [loadingDetail, setLoadingDetail] = useState(false);

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        setLoading(true);
        try {
            const [data, confirmed, corrections] = await Promise.all([
                getHistory(),
                getConfirmedProcesses(),
                getLatestCorrections(),
            ]);
            setHistory(data);
            setConfirmedIds(new Set(confirmed.confirmed_processes || []));
            setPhaseCorrections(corrections.corrections || {});
        } catch (error) {
            console.error('Error fetching history:', error);
            setHistory([]);
        } finally {
            setLoading(false);
        }
    };

    const handleClear = async () => {
        if (!window.confirm('Tem certeza que deseja limpar todo o histórico?')) return;
        try {
            await clearHistory();
            setHistory([]);
            setExpandedId(null);
            setConfirmedIds(new Set());
            setPhaseCorrections({});
            setInlineDetailId(null);
            setInlineDetailData(null);
            toast.success('Histórico limpo com sucesso!');
        } catch {
            toast.error('Erro ao limpar histórico.');
        }
    };

    const handleCopyNumber = (number, event) => {
        event.stopPropagation();
        navigator.clipboard.writeText(number).then(() => {
            toast.success('Número copiado!');
        }).catch(() => {
            toast.error('Erro ao copiar número.');
        });
    };

    const handleViewProcess = async (item, event) => {
        event.stopPropagation();
        // Toggle: se já está expandido, recolher
        if (inlineDetailId === item.id) {
            setInlineDetailId(null);
            setInlineDetailData(null);
            return;
        }
        setLoadingDetail(true);
        setInlineDetailId(item.id);
        setInlineDetailData(null);
        try {
            toast.loading('Buscando processo...', { id: 'search' });
            const result = await searchProcess(item.number);
            toast.success('Processo encontrado!', { id: 'search' });
            setInlineDetailData(result);
        } catch (error) {
            toast.error('Erro ao buscar processo.', { id: 'search' });
            console.error('Error fetching process:', error);
            setInlineDetailId(null);
        } finally {
            setLoadingDetail(false);
        }
    };

    const filtered = history.filter(item => {
        if (filter === 'all') return true;
        if (filter === 'found') return item.status === 'found' || !item.status;
        if (filter === 'not_found') return item.status === 'not_found';
        if (filter === 'error') return item.status === 'api_error' || item.status === 'network_error';
        return true;
    });

    const counts = {
        all: history.length,
        found: history.filter(i => i.status === 'found' || !i.status).length,
        not_found: history.filter(i => i.status === 'not_found').length,
        error: history.filter(i => i.status === 'api_error' || i.status === 'network_error').length,
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-extrabold text-gray-900">{labels.nav.history}</h2>
                    <p className="text-gray-500 mt-2">Acompanhe suas últimas consultas realizadas.</p>
                </div>
                {history.length > 0 && (
                    <button
                        onClick={handleClear}
                        className="flex items-center space-x-2 text-red-600 hover:text-red-700 font-bold px-4 py-2 border border-red-200 rounded-lg bg-red-50 transition-colors"
                    >
                        <Trash2 className="h-4 w-4" />
                        <span>Limpar Histórico</span>
                    </button>
                )}
            </div>

            {/* Filtros */}
            {history.length > 0 && (
                <div className="flex gap-2 flex-wrap">
                    {FILTERS.map(f => (
                        <button
                            key={f.value}
                            onClick={() => setFilter(f.value)}
                            className={`px-3 py-1.5 rounded-full text-sm font-semibold border transition-colors ${
                                filter === f.value
                                    ? 'bg-indigo-600 text-white border-indigo-600'
                                    : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300'
                            }`}
                        >
                            {f.label}
                            <span className={`ml-1.5 text-xs px-1.5 py-0.5 rounded-full ${
                                filter === f.value ? 'bg-indigo-500 text-white' : 'bg-gray-100 text-gray-500'
                            }`}>
                                {counts[f.value]}
                            </span>
                        </button>
                    ))}
                </div>
            )}

            {loading ? (
                <div className="flex justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                </div>
            ) : filtered.length === 0 ? (
                <div className="bg-white rounded-2xl border-2 border-dashed border-gray-200 p-12 text-center">
                    <div className="inline-flex items-center justify-center p-4 bg-gray-50 rounded-full mb-4">
                        <Clock className="h-8 w-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900">
                        {filter === 'all' ? 'Nenhum histórico encontrado' : 'Nenhum registro neste filtro'}
                    </h3>
                    <p className="text-gray-500 mt-1">
                        {filter === 'all'
                            ? 'As consultas que você realizar aparecerão aqui.'
                            : 'Tente selecionar outro filtro.'}
                    </p>
                </div>
            ) : (
                <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
                    <ul className="divide-y divide-gray-100">
                        {filtered.map((item) => {
                            const isFound = item.status === 'found' || !item.status;
                            const tribunal = item.court?.split(' - ')[0] || item.tribunal_expected || null;
                            const isExpanded = expandedId === item.id;
                            const hasLog = !!item.classification_log;
                            const isCorrected = !!phaseCorrections[item.number];
                            // Use classification_log phase if available (correct/normalized phase), otherwise fall back to item.phase
                            const classificationLogPhase = (() => {
                              if (!item.classification_log) return null;
                              const log = typeof item.classification_log === 'string'
                                ? JSON.parse(item.classification_log)
                                : item.classification_log;
                              return log?.phase;
                            })();
                            const displayPhase = phaseCorrections[item.number] || classificationLogPhase || item.phase;
                            const isInlineOpen = inlineDetailId === item.id;
                            return (
                                <li key={item.id} className="hover:bg-gray-50/50 transition-colors">
                                    <div className="px-6 py-4 flex items-center justify-between gap-4">
                                        <div className="flex items-center gap-4 flex-1 min-w-0">
                                            <div className={`p-2 rounded-lg shrink-0 ${isFound ? 'bg-indigo-50' : 'bg-red-50'}`}>
                                                <FileText className={`h-5 w-5 ${isFound ? 'text-indigo-600' : 'text-red-400'}`} />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2 flex-wrap">
                                                    <p className="font-bold text-gray-900 font-mono text-sm">
                                                        {item.number}
                                                    </p>
                                                    <StatusBadge status={item.status || 'found'} />
                                                    {isFound && item.phase && (
                                                        <PhaseBadge
                                                            phase={displayPhase}
                                                            corrected={isCorrected}
                                                            confirmed={confirmedIds.has(item.number)}
                                                            onEdit={() => setEditingItem(item)}
                                                            onConfirm={async () => {
                                                                try {
                                                                    await confirmPhase(item.number, displayPhase);
                                                                    setConfirmedIds(prev => new Set([...prev, item.number]));
                                                                    toast.success('Fase confirmada como correta!');
                                                                } catch {
                                                                    toast.error('Erro ao confirmar fase.');
                                                                }
                                                            }}
                                                        />
                                                    )}
                                                    {isFound && item.classification?.stage && (
                                                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${getStageColorClasses(item.classification.stage)}`}>
                                                            {item.classification.stage_label || STAGES[item.classification.stage]?.label}
                                                            {item.classification.substage && (
                                                                <span className="ml-1 font-normal opacity-75">
                                                                    / {item.classification.substage_label || SUBSTAGES[item.classification.substage]?.label}
                                                                </span>
                                                            )}
                                                        </span>
                                                    )}
                                                </div>
                                                <div className="text-xs text-gray-500 mt-1 space-y-0.5">
                                                    {isFound && tribunal && (
                                                        <p className="truncate">{item.court || tribunal}</p>
                                                    )}
                                                    {!isFound && tribunal && (
                                                        <p className="truncate">
                                                            Tribunal esperado: <span className="font-semibold text-gray-700">{tribunal}</span>
                                                        </p>
                                                    )}
                                                    {!isFound && item.error_message && (
                                                        <p className="text-red-500 truncate" title={item.error_message}>
                                                            {item.error_message}
                                                        </p>
                                                    )}
                                                    <p>{new Date(item.created_at).toLocaleString('pt-BR')}</p>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2 shrink-0">
                                            {hasLog && (
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setExpandedId(isExpanded ? null : item.id);
                                                    }}
                                                    className={`p-2 rounded-lg transition-colors ${
                                                        isExpanded
                                                            ? 'text-indigo-600 bg-indigo-50'
                                                            : 'text-gray-400 hover:text-indigo-600 hover:bg-indigo-50'
                                                    }`}
                                                    title="Ver fundamentos da classificação"
                                                    aria-label="Ver fundamentos da classificação"
                                                    aria-expanded={isExpanded}
                                                >
                                                    {isExpanded
                                                        ? <ChevronUp className="h-4 w-4" />
                                                        : <ChevronDown className="h-4 w-4" />
                                                    }
                                                </button>
                                            )}
                                            <button
                                                onClick={(e) => handleCopyNumber(item.number, e)}
                                                className="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                                                title="Copiar número do processo"
                                                aria-label="Copiar número do processo"
                                            >
                                                <Copy className="h-4 w-4" />
                                            </button>
                                            {isFound && (
                                                <button
                                                    onClick={(e) => handleViewProcess(item, e)}
                                                    className={`flex items-center gap-1.5 px-3 py-2 text-sm font-medium border rounded-lg transition-colors ${
                                                        isInlineOpen
                                                            ? 'text-white bg-indigo-600 border-indigo-600'
                                                            : 'text-indigo-600 hover:text-white hover:bg-indigo-600 border-indigo-200'
                                                    }`}
                                                    title={isInlineOpen ? 'Recolher detalhes' : 'Ver detalhes do processo'}
                                                    aria-label={isInlineOpen ? 'Recolher detalhes' : 'Ver detalhes do processo'}
                                                >
                                                    {isInlineOpen
                                                        ? <><ChevronUp className="h-4 w-4" /><span>Recolher</span></>
                                                        : <><ExternalLink className="h-4 w-4" /><span>Ver Detalhes</span></>
                                                    }
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                    {isExpanded && hasLog && (
                                        <ClassificationTrace log={item.classification_log} classification={item.classification} />
                                    )}
                                    {/* Inline ProcessDetails */}
                                    {isInlineOpen && (
                                        <div className="border-t border-gray-200 bg-gray-50/50 px-4 py-4">
                                            {loadingDetail ? (
                                                <div className="flex justify-center py-8">
                                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
                                                </div>
                                            ) : inlineDetailData ? (
                                                <Suspense fallback={<div className="animate-pulse h-48 bg-gray-100 rounded-lg" />}>
                                                    <ProcessDetails data={inlineDetailData} />
                                                </Suspense>
                                            ) : null}
                                        </div>
                                    )}
                                </li>
                            );
                        })}
                    </ul>
                </div>
            )}

            {/* Modal de Edição de Fase */}
            {editingItem && (
                <PhaseEditModal
                    processNumber={editingItem.number}
                    currentPhase={phaseCorrections[editingItem.number] || editingItem.phase}
                    classificationLog={typeof editingItem.classification_log === 'string' ? JSON.parse(editingItem.classification_log) : editingItem.classification_log}
                    sourceTab="history"
                    onClose={() => setEditingItem(null)}
                    onSuccess={(newPhaseCode) => {
                        setPhaseCorrections(prev => ({
                            ...prev,
                            [editingItem.number]: newPhaseCode,
                        }));
                        toast.success('Fase corrigida com sucesso!');
                        setEditingItem(null);
                    }}
                />
            )}
        </div>
    );
}

export default HistoryTab;
