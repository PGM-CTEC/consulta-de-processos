import React, { useState, useEffect } from 'react';
import { Clock, Trash2, ChevronRight, AlertCircle, FileText } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getHistory, clearHistory } from '../services/api';

function HistoryTab({ labels }) {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        setLoading(true);
        try {
            // Note: API endpoints to be implemented in backend
            const data = await getHistory();
            setHistory(data);
        } catch (error) {
            console.error('Error fetching history:', error);
            // Fallback while backend is not ready
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
                                <button className="w-full px-6 py-4 flex items-center justify-between text-left group">
                                    <div className="flex items-center space-x-4">
                                        <div className="bg-indigo-50 p-2 rounded-lg group-hover:bg-indigo-100 transition-colors">
                                            <FileText className="h-5 w-5 text-indigo-600" />
                                        </div>
                                        <div>
                                            <p className="font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">
                                                {item.number}
                                            </p>
                                            <div className="flex items-center space-x-2 text-xs text-gray-500 mt-1">
                                                <span>{item.court}</span>
                                                <span>•</span>
                                                <span>{new Date(item.created_at).toLocaleString()}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <ChevronRight className="h-5 w-5 text-gray-400 group-hover:text-indigo-600 transform group-hover:translate-x-1 transition-all" />
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default HistoryTab;
