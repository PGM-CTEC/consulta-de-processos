import React, { useState, useEffect } from 'react';
import { AlertTriangle, Activity, Zap, TrendingUp, RefreshCw, Loader2, AlertCircle, BarChart3 } from 'lucide-react';
import { getMetrics } from '../services/api';
import './PerformanceDashboard.css';

const PerformanceDashboard = () => {
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [refreshInterval, setRefreshInterval] = useState(5); // seconds
    const [lastUpdate, setLastUpdate] = useState(null);

    const loadMetrics = async () => {
        try {
            setError(null);
            const data = await getMetrics(24);
            setMetrics(data);
            setLastUpdate(new Date());
        } catch (err) {
            console.error('Error loading metrics:', err);
            setError('Falha ao carregar métricas de performance.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadMetrics();
        const interval = setInterval(loadMetrics, refreshInterval * 1000);
        return () => clearInterval(interval);
    }, [refreshInterval]);

    if (loading && !metrics) {
        return (
            <div className="flex items-center justify-center min-h-96">
                <Loader2 className="h-12 w-12 animate-spin text-indigo-600" />
            </div>
        );
    }

    const current = metrics?.current;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Activity className="h-8 w-8 text-indigo-600" />
                    <h1 className="text-3xl font-bold text-gray-900">Performance Monitoring</h1>
                </div>
                <div className="flex items-center gap-3">
                    <select
                        value={refreshInterval}
                        onChange={(e) => setRefreshInterval(Number(e.target.value))}
                        className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                        <option value={5}>Refresh: 5s</option>
                        <option value={10}>Refresh: 10s</option>
                        <option value={30}>Refresh: 30s</option>
                    </select>
                    <button
                        onClick={loadMetrics}
                        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                        title="Refresh now"
                    >
                        <RefreshCw className="h-5 w-5 text-gray-600" />
                    </button>
                </div>
            </div>

            {/* Last Update Info */}
            {lastUpdate && (
                <p className="text-sm text-gray-500">
                    Última atualização: {lastUpdate.toLocaleTimeString()}
                </p>
            )}

            {/* Error State */}
            {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-6 flex items-center">
                    <AlertCircle className="h-6 w-6 text-red-600 mr-3" />
                    <div>
                        <h3 className="font-bold text-red-900">Erro ao carregar métricas</h3>
                        <p className="text-red-700 text-sm">{error}</p>
                    </div>
                </div>
            )}

            {/* No Data State */}
            {!current && !error && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 flex items-center">
                    <AlertTriangle className="h-6 w-6 text-yellow-600 mr-3" />
                    <div>
                        <h3 className="font-bold text-yellow-900">Sem dados disponíveis</h3>
                        <p className="text-yellow-700 text-sm">Aguardando coleta de métricas...</p>
                    </div>
                </div>
            )}

            {/* Current Metrics Cards */}
            {current && (
                <>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {/* Latency Cards */}
                        <MetricCard
                            title="P50 Latency"
                            value={`${current.latency_p50}ms`}
                            icon={<Zap className="h-6 w-6 text-blue-600" />}
                            status={current.latency_p50 < 1000 ? 'good' : 'warning'}
                        />
                        <MetricCard
                            title="P95 Latency"
                            value={`${current.latency_p95}ms`}
                            icon={<TrendingUp className="h-6 w-6 text-orange-600" />}
                            status={current.latency_p95 < 3000 ? 'good' : 'warning'}
                        />
                        <MetricCard
                            title="P99 Latency"
                            value={`${current.latency_p99}ms`}
                            icon={<AlertTriangle className="h-6 w-6 text-red-600" />}
                            status={current.latency_p99 < 5000 ? 'good' : 'critical'}
                        />

                        {/* Throughput */}
                        <MetricCard
                            title="Throughput"
                            value={`${current.throughput} req/s`}
                            icon={<BarChart3 className="h-6 w-6 text-green-600" />}
                            status="info"
                        />

                        {/* Error Rate */}
                        <MetricCard
                            title="Error Rate"
                            value={`${current.error_rate}%`}
                            icon={<AlertCircle className="h-6 w-6 text-red-600" />}
                            status={current.error_rate < 1 ? 'good' : current.error_rate < 5 ? 'warning' : 'critical'}
                        />

                        {/* Cache Hit Ratio */}
                        <MetricCard
                            title="Cache Hit Ratio"
                            value={`${current.cache_hit_ratio}%`}
                            icon={<Activity className="h-6 w-6 text-purple-600" />}
                            status={current.cache_hit_ratio > 70 ? 'good' : 'warning'}
                        />

                        {/* DB Query Time */}
                        <MetricCard
                            title="Avg DB Query"
                            value={`${current.db_query_time}ms`}
                            icon={<Zap className="h-6 w-6 text-indigo-600" />}
                            status={current.db_query_time < 100 ? 'good' : 'warning'}
                        />
                    </div>

                    {/* Alerts Section */}
                    {metrics?.alerts && metrics.alerts.length > 0 && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
                            <h2 className="text-lg font-bold text-yellow-900 mb-4 flex items-center gap-2">
                                <AlertTriangle className="h-5 w-5" />
                                Performance Alerts ({metrics.alerts.length})
                            </h2>
                            <div className="space-y-3">
                                {metrics.alerts.slice(0, 5).map((alert, idx) => (
                                    <div
                                        key={idx}
                                        className={`p-4 rounded-lg ${
                                            alert.severity === 'critical'
                                                ? 'bg-red-100 border border-red-300'
                                                : alert.severity === 'warning'
                                                ? 'bg-yellow-100 border border-yellow-300'
                                                : 'bg-blue-100 border border-blue-300'
                                        }`}
                                    >
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <p className="font-bold text-sm">
                                                    {alert.type}
                                                </p>
                                                <p className="text-sm mt-1">{alert.message}</p>
                                            </div>
                                            <span className={`text-xs font-bold px-2 py-1 rounded ${
                                                alert.severity === 'critical'
                                                    ? 'bg-red-200 text-red-900'
                                                    : alert.severity === 'warning'
                                                    ? 'bg-yellow-200 text-yellow-900'
                                                    : 'bg-blue-200 text-blue-900'
                                            }`}>
                                                {alert.severity.toUpperCase()}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

// Metric Card Component
const MetricCard = ({ title, value, icon, status }) => {
    const statusColors = {
        good: 'border-green-300 bg-green-50',
        warning: 'border-yellow-300 bg-yellow-50',
        critical: 'border-red-300 bg-red-50',
        info: 'border-blue-300 bg-blue-50',
    };

    return (
        <div className={`rounded-xl p-6 border-2 ${statusColors[status] || statusColors.info}`}>
            <div className="flex items-start justify-between mb-4">
                <h3 className="text-sm font-bold text-gray-700">{title}</h3>
                {icon}
            </div>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            <p className={`text-xs font-bold mt-2 ${
                status === 'good' ? 'text-green-700' :
                status === 'warning' ? 'text-yellow-700' :
                status === 'critical' ? 'text-red-700' :
                'text-blue-700'
            }`}>
                {status === 'good' ? '✅ Normal' :
                 status === 'warning' ? '⚠️ Warning' :
                 status === 'critical' ? '🔴 Critical' :
                 'ℹ️ Info'}
            </p>
        </div>
    );
};

export default PerformanceDashboard;
