import { useState, useEffect } from 'react';
import { Clock, Trash2, Copy, ExternalLink, FileText, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getHistory, clearHistory, searchProcess } from '../services/api';

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

function HistoryTab({ labels, onProcessView }) {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');

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
                        {filtered.map((item, index) => {
                            const isFound = item.status === 'found' || !item.status;
                            const tribunal = item.court?.split(' - ')[0] || item.tribunal_expected || null;
                            return (
                                <li key={index} className="hover:bg-gray-50 transition-colors">
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
                                </li>
                            );
                        })}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default HistoryTab;
