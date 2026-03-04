import React, { useState, useEffect } from 'react';
import { Clock, Trash2, Copy, ExternalLink, FileText } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getHistory, clearHistory, searchProcess } from '../services/api';

function HistoryTab({ labels, onProcessView }) {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

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

            // Se houver callback para visualizar processo
            if (onProcessView) {
                onProcessView(result);
            }
        } catch (error) {
            toast.error('Erro ao buscar processo.', { id: 'search' });
            console.error('Error fetching process:', error);
        }
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

            {loading ? (
                <div className="flex justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                </div>
            ) : history.length === 0 ? (
                <div className="bg-white rounded-2xl border-2 border-dashed border-gray-200 p-12 text-center">
                    <div className="inline-flex items-center justify-center p-4 bg-gray-50 rounded-full mb-4">
                        <Clock className="h-8 w-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900">Nenhum histórico encontrado</h3>
                    <p className="text-gray-500 mt-1">As consultas que você realizar aparecerão aqui.</p>
                </div>
            ) : (
                <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
                    <ul className="divide-y divide-gray-100">
                        {history.map((item, index) => (
                            <li key={index} className="hover:bg-gray-50 transition-colors">
                                <div className="px-6 py-4 flex items-center justify-between">
                                    <div className="flex items-center space-x-4 flex-1">
                                        <div className="bg-indigo-50 p-2 rounded-lg">
                                            <FileText className="h-5 w-5 text-indigo-600" />
                                        </div>
                                        <div className="flex-1">
                                            <p className="font-bold text-gray-900 font-mono text-sm">
                                                {item.number}
                                            </p>
                                            <div className="flex items-center space-x-2 text-xs text-gray-500 mt-1">
                                                <span className="truncate max-w-xs">{item.court || 'Tribunal não especificado'}</span>
                                                <span>•</span>
                                                <span>{new Date(item.created_at).toLocaleString('pt-BR')}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2 ml-4">
                                        <button
                                            onClick={(e) => handleCopyNumber(item.number, e)}
                                            className="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                                            title="Copiar número do processo"
                                            aria-label="Copiar número do processo"
                                        >
                                            <Copy className="h-4 w-4" />
                                        </button>
                                        <button
                                            onClick={(e) => handleViewProcess(item.number, e)}
                                            className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-indigo-600 hover:text-white hover:bg-indigo-600 border border-indigo-200 rounded-lg transition-colors"
                                            title="Ver detalhes do processo"
                                            aria-label="Ver detalhes do processo"
                                        >
                                            <ExternalLink className="h-4 w-4" />
                                            <span>Ver Detalhes</span>
                                        </button>
                                    </div>
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default HistoryTab;
