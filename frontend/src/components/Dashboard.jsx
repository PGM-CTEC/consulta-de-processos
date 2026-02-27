import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Database, Calendar, RefreshCw, Loader2, AlertCircle } from 'lucide-react';
import { getStats } from '../services/api';
import { getPhaseColorClasses, getPhaseDisplayName } from '../utils/phaseColors';

const Dashboard = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadStats = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getStats();
            setStats(data);
        } catch (err) {
            console.error('Error loading stats:', err);
            setError('Falha ao carregar estatísticas do banco de dados.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadStats();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-96">
                <Loader2 className="h-12 w-12 animate-spin text-indigo-600" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-xl p-6 flex items-center">
                <AlertCircle className="h-6 w-6 text-red-600 mr-3" />
                <div>
                    <h3 className="font-bold text-red-900">Erro ao carregar dados</h3>
                    <p className="text-red-700 text-sm">{error}</p>
                </div>
            </div>
        );
    }

    if (!stats || stats.total_processes === 0) {
        return (
            <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-xl p-12 text-center">
                <Database className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-600 mb-2">Banco de Dados Vazio</h3>
                <p className="text-gray-500">
                    Consulte alguns processos primeiro para visualizar estatísticas e análises.
                </p>
            </div>
        );
    }

    const maxTribunalCount = Math.max(...stats.tribunals.map(t => t.count), 1);
    const maxPhaseCount = Math.max(...stats.phases.map(p => p.count), 1);
    const maxTimelineCount = Math.max(...stats.timeline.map(t => t.count), 1);

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
                <div className="p-6 bg-gradient-to-r from-indigo-600 to-violet-600 flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-bold text-white flex items-center">
                            <BarChart3 className="mr-2 h-6 w-6" />
                            Analytics & Business Intelligence
                        </h2>
                        <p className="text-indigo-100 text-sm mt-1">
                            Estatísticas do banco de dados local
                        </p>
                    </div>
                    <button
                        onClick={loadStats}
                        className="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-lg font-bold transition-colors flex items-center space-x-2"
                    >
                        <RefreshCw className="h-4 w-4" />
                        <span>Atualizar</span>
                    </button>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-blue-600 text-sm font-bold uppercase tracking-wide">Total de Processos</p>
                                <p className="text-4xl font-extrabold text-blue-900 mt-2">{stats.total_processes.toLocaleString()}</p>
                            </div>
                            <Database className="h-12 w-12 text-blue-400" />
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-green-600 text-sm font-bold uppercase tracking-wide">Total de Movimentos</p>
                                <p className="text-4xl font-extrabold text-green-900 mt-2">{stats.total_movements.toLocaleString()}</p>
                            </div>
                            <TrendingUp className="h-12 w-12 text-green-400" />
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-purple-600 text-sm font-bold uppercase tracking-wide">Última Atualização</p>
                                <p className="text-lg font-bold text-purple-900 mt-2">
                                    {stats.last_updated ? new Date(stats.last_updated).toLocaleDateString('pt-BR') : 'N/A'}
                                </p>
                                <p className="text-xs text-purple-600 mt-1">
                                    {stats.last_updated ? new Date(stats.last_updated).toLocaleTimeString('pt-BR') : ''}
                                </p>
                            </div>
                            <Calendar className="h-12 w-12 text-purple-400" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Tribunals Chart */}
                <section className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6" aria-labelledby="tribunals-title">
                    <h2 id="tribunals-title" className="text-lg font-bold text-gray-900 mb-4">Processos por Tribunal</h2>
                    {stats.tribunals.length > 0 ? (
                        <ul className="space-y-3 list-none p-0">
                            {stats.tribunals.map((tribunal, idx) => (
                                <li key={idx} className="space-y-1">
                                    <div className="flex justify-between items-center text-sm">
                                        <span className="font-semibold text-gray-700 truncate mr-2">{tribunal.tribunal_name}</span>
                                        <span className="font-bold text-indigo-600">{tribunal.count.toLocaleString()}</span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                                        <div
                                            className="bg-gradient-to-r from-indigo-500 to-indigo-600 h-3 rounded-full transition-all duration-500"
                                            style={{ width: `${(tribunal.count / maxTribunalCount) * 100}%` }}
                                        />
                                    </div>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-gray-600 text-sm italic">Nenhum dado disponível</p>
                    )}
                </section>

                {/* Phases Chart */}
                <section className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6" aria-labelledby="phases-title">
                    <h2 id="phases-title" className="text-lg font-bold text-gray-900 mb-4">Processos por Fase</h2>
                    {stats.phases.length > 0 ? (
                        <ul className="space-y-3 list-none p-0">
                            {stats.phases.map((phase, idx) => (
                                <li key={idx} className="space-y-1">
                                    <div className="flex justify-between items-center text-sm">
                                        <div className="flex items-center space-x-2">
                                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${getPhaseColorClasses(phase.phase, phase.class_nature)}`}>
                                                {getPhaseDisplayName(phase.phase, phase.class_nature)}
                                            </span>
                                        </div>
                                        <span className="font-bold text-indigo-600">{phase.count.toLocaleString()}</span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                                        <div
                                            className="bg-gradient-to-r from-violet-500 to-violet-600 h-3 rounded-full transition-all duration-500"
                                            style={{ width: `${(phase.count / maxPhaseCount) * 100}%` }}
                                        />
                                    </div>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-gray-600 text-sm italic">Nenhum dado disponível</p>
                    )}
                </section>
            </div>

            {/* Timeline Chart */}
            {stats.timeline && stats.timeline.length > 0 && (
                <section className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6" aria-labelledby="timeline-title">
                    <h2 id="timeline-title" className="text-lg font-bold text-gray-900 mb-4">Distribuição Temporal (Últimos 12 meses)</h2>
                    <div className="flex items-end justify-between space-x-2 h-64">
                        {stats.timeline.map((item, idx) => {
                            const height = (item.count / maxTimelineCount) * 100;
                            return (
                                <div key={idx} className="flex-1 flex flex-col items-center">
                                    <div className="w-full flex flex-col items-center justify-end h-full pb-2">
                                        <span className="text-xs font-bold text-indigo-600 mb-1">{item.count}</span>
                                        <div
                                            className="w-full bg-gradient-to-t from-indigo-500 to-indigo-400 rounded-t-lg hover:from-indigo-600 hover:to-indigo-500 transition-all cursor-pointer"
                                            style={{ height: `${height}%` }}
                                            title={`${item.month}: ${item.count} processos`}
                                        />
                                    </div>
                                    <span className="text-xs text-gray-600 font-semibold mt-2 transform -rotate-45 origin-top-left">
                                        {item.month}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </section>
            )}
        </div>
    );
};

export default Dashboard;
