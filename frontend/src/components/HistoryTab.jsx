import { useState, useEffect, useCallback } from 'react';
import { Clock, Trash2, Copy, ExternalLink, FileText, CheckCircle, XCircle, AlertTriangle, ChevronDown, ChevronUp, Pencil } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getHistory, clearHistory, searchProcess } from '../services/api';
import { PHASE_BY_CODE } from '../constants/phases';
import { getPhaseColorClasses } from '../utils/phaseColors';
import PhaseEditModal from './PhaseEditModal';

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

const RULE_LABELS = {
    P1_arquivamento: 'Arquivamento encontrado (prioridade máxima)',
    P2_transito_em_julgado: 'Certidão/Trânsito em Julgado detectado',
    P3_sentenca_com_remessa_posterior: 'Sentença + remessa posterior',
    P3_sentenca_sem_transito: 'Sentença sem trânsito em julgado',
    P4_remessa_sem_sentenca: 'Remessa/recurso sem sentença prévia',
    P5_suspensao: 'Suspensão/sobrestamento detectado',
    P6_fallback_antes_sentenca: 'Nenhuma âncora encontrada (fase inicial)',
    E1_arquivamento: 'Arquivamento em execução',
    E2_suspensao: 'Suspensão em execução',
    E3_fallback: 'Execução em andamento (nenhuma âncora)',
    empty_list_fallback: 'Lista de movimentos vazia',
    fusion_not_found: 'Processo não encontrado no Fusion/PAV',
    fusion_error: 'Erro ao consultar Fusion/PAV',
    fusion_unavailable: 'Serviço Fusion/PAV não configurado',
};

const BRANCH_LABELS = {
    conhecimento: 'Conhecimento',
    execucao: 'Execução',
};

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

function PhaseBadge({ phase, corrected, onEdit }) {
    if (!phase || phase === 'Indefinido') {
        return (
            <div className="flex items-center gap-1">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-500 border border-gray-200">
                    Fase Indefinida
                </span>
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
                    ✓
                </span>
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

function ClassificationTrace({ log }) {
    if (!log) return null;

    return (
        <div className="px-6 pb-4 bg-gray-50 border-t border-gray-100 animate-in fade-in duration-200">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 py-3 text-xs">
                <div>
                    <span className="text-gray-400 font-semibold uppercase tracking-wide block">Branch</span>
                    <p className="text-gray-700 font-medium mt-0.5">
                        {BRANCH_LABELS[log.branch] || log.branch || 'N/A'}
                    </p>
                </div>
                <div>
                    <span className="text-gray-400 font-semibold uppercase tracking-wide block">Movimentos</span>
                    <p className="text-gray-700 mt-0.5">{log.total_movimentos ?? 0}</p>
                </div>
                <div>
                    <span className="text-gray-400 font-semibold uppercase tracking-wide block">Classe</span>
                    <p className="text-gray-700 mt-0.5 truncate" title={log.classe_normalizada || ''}>
                        {log.classe_normalizada || 'N/A'}
                    </p>
                </div>
                <div>
                    <span className="text-gray-400 font-semibold uppercase tracking-wide block">Regra</span>
                    <p className="text-gray-700 mt-0.5 font-medium">
                        {RULE_LABELS[log.rule_applied] || log.rule_applied || 'N/A'}
                    </p>
                </div>
            </div>

            {log.decisive_movement && (
                <div className="py-2 border-t border-gray-200 text-xs">
                    <span className="text-gray-400 font-semibold uppercase tracking-wide block">Movimento decisivo</span>
                    <p className="text-gray-800 font-semibold mt-0.5">
                        {log.decisive_movement}
                        {log.decisive_movement_date && (
                            <span className="text-gray-500 font-normal ml-2">
                                ({new Date(log.decisive_movement_date).toLocaleDateString('pt-BR')})
                            </span>
                        )}
                    </p>
                </div>
            )}

            {log.anchor_matches && Object.keys(log.anchor_matches).length > 0 && (
                <div className="py-2 border-t border-gray-200 text-xs">
                    <span className="text-gray-400 font-semibold uppercase tracking-wide block mb-1">
                        Âncoras detectadas
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                        {Object.entries(log.anchor_matches).map(([key, idx]) => (
                            <span
                                key={key}
                                className={`px-2 py-0.5 rounded text-xs font-mono ${
                                    idx !== null
                                        ? 'bg-green-50 text-green-700 border border-green-200'
                                        : 'bg-gray-100 text-gray-400 border border-gray-200'
                                }`}
                            >
                                {key}: {idx !== null ? `#${idx}` : '—'}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

function HistoryTab({ labels, onProcessView }) {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [expandedId, setExpandedId] = useState(null);
    const [phaseCorrections, setPhaseCorrections] = useState({});
    const [editingItem, setEditingItem] = useState(null);

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        setLoading(true);
        try {
            const data = await getHistory();
            setHistory(data);
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

    const handleViewProcess = async (number, event) => {
        event.stopPropagation();
        try {
            toast.loading('Buscando processo...', { id: 'search' });
            const result = await searchProcess(number);
            toast.success('Processo encontrado!', { id: 'search' });
            if (onProcessView) onProcessView(result);
        } catch (error) {
            toast.error('Erro ao buscar processo.', { id: 'search' });
            console.error('Error fetching process:', error);
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
                                                            phase={phaseCorrections[item.id] || item.phase}
                                                            corrected={!!phaseCorrections[item.id]}
                                                            onEdit={() => setEditingItem(item)}
                                                        />
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
                                                    title="Ver log de classificação"
                                                    aria-label="Ver log de classificação"
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
                                                    onClick={(e) => handleViewProcess(item.number, e)}
                                                    className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-indigo-600 hover:text-white hover:bg-indigo-600 border border-indigo-200 rounded-lg transition-colors"
                                                    title="Ver detalhes do processo"
                                                    aria-label="Ver detalhes do processo"
                                                >
                                                    <ExternalLink className="h-4 w-4" />
                                                    <span>Ver Detalhes</span>
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                    {isExpanded && hasLog && (
                                        <ClassificationTrace log={item.classification_log} />
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
                    currentPhase={phaseCorrections[editingItem.id] || editingItem.phase}
                    classificationLog={typeof editingItem.classification_log === 'string' ? JSON.parse(editingItem.classification_log) : editingItem.classification_log}
                    sourceTab="history"
                    onClose={() => setEditingItem(null)}
                    onSuccess={(newPhaseCode) => {
                        setPhaseCorrections(prev => ({
                            ...prev,
                            [editingItem.id]: newPhaseCode,
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
