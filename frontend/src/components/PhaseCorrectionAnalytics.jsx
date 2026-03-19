import { useState, useEffect } from 'react';
import { Database, AlertCircle, CheckCircle, TrendingUp, RefreshCw, Loader2 } from 'lucide-react';
import { getPhaseCorrectionsAnalytics } from '../services/api';
import { getPhaseColorClasses } from '../utils/phaseColors';
import { PHASE_BY_CODE, PHASE_BY_NAME } from '../constants/phases';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { toast } from 'react-hot-toast';

function getPhaseLabel(fase) {
    if (!fase || fase === 'Indefinido') return 'Indefinido';
    const code = String(fase).padStart(2, '0');
    if (PHASE_BY_CODE[code]) return `${code} — ${PHASE_BY_CODE[code].name}`;
    if (PHASE_BY_NAME[fase]) return `${PHASE_BY_NAME[fase].code} — ${fase}`;
    return fase;
}

const PhaseCorrectionAnalytics = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadAnalytics = async () => {
        setLoading(true);
        setError(null);
        try {
            const result = await getPhaseCorrectionsAnalytics();
            setData(result);
        } catch (err) {
            console.error('Erro ao carregar análise de correções:', err);
            const message = err.response?.data?.detail || 'Falha ao carregar análise de correções.';
            setError(message);
            toast.error(message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadAnalytics();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-96">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 animate-spin text-indigo-600 mx-auto mb-4" />
                    <p className="text-gray-600 dark:text-gray-400">Carregando análise de correções...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-96">
                <div className="text-center bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-xl p-6 max-w-md">
                    <AlertCircle className="h-12 w-12 text-red-600 dark:text-red-400 mx-auto mb-4" />
                    <p className="text-red-800 dark:text-red-300 font-medium">{error}</p>
                    <Button onClick={loadAnalytics} className="mt-4">Tentar novamente</Button>
                </div>
            </div>
        );
    }

    if (!data) {
        return null;
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                        Análise de Correções
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400">
                        Estatísticas da classificação automática de fases e correções manuais
                    </p>
                </div>
                <Button
                    onClick={loadAnalytics}
                    variant="outline"
                    size="icon"
                    className="rounded-lg"
                    aria-label="Atualizar dados"
                >
                    <RefreshCw className="h-5 w-5" />
                </Button>
            </div>

            {/* Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Total Consultados */}
                <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-900/10 border-blue-200 dark:border-blue-800">
                    <CardHeader className="pb-2">
                        <CardTitle className="flex items-center space-x-2 text-sm font-medium text-blue-700 dark:text-blue-300">
                            <Database className="h-4 w-4" />
                            <span>Processos Consultados</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-blue-900 dark:text-blue-100">
                            {data.total_consultados.toLocaleString('pt-BR')}
                        </div>
                    </CardContent>
                </Card>

                {/* Total Corrigidos (Erros) */}
                <Card className="bg-gradient-to-br from-orange-50 to-red-100 dark:from-red-900/20 dark:to-red-900/10 border-orange-200 dark:border-red-800">
                    <CardHeader className="pb-2">
                        <CardTitle className="flex items-center space-x-2 text-sm font-medium text-orange-700 dark:text-orange-300">
                            <AlertCircle className="h-4 w-4" />
                            <span>Erros Detectados</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-orange-900 dark:text-orange-100">
                            {data.total_corrigidos.toLocaleString('pt-BR')}
                        </div>
                        <p className="text-xs text-orange-700 dark:text-orange-300 mt-1">
                            {data.total_consultados > 0
                                ? `${((data.total_corrigidos / data.total_consultados) * 100).toFixed(1)}% de erro`
                                : '0%'}
                        </p>
                    </CardContent>
                </Card>

                {/* Total Sem Correção (Acertos) */}
                <Card className="bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-900/20 dark:to-emerald-900/10 border-green-200 dark:border-emerald-800">
                    <CardHeader className="pb-2">
                        <CardTitle className="flex items-center space-x-2 text-sm font-medium text-green-700 dark:text-emerald-300">
                            <CheckCircle className="h-4 w-4" />
                            <span>Classificações Corretas</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-green-900 dark:text-emerald-100">
                            {data.total_sem_correcao.toLocaleString('pt-BR')}
                        </div>
                        <p className="text-xs text-green-700 dark:text-green-300 mt-1">
                            {data.total_confirmados > 0
                                ? `${data.total_confirmados} confirmadas manualmente`
                                : 'nenhuma confirmação manual'}
                        </p>
                    </CardContent>
                </Card>

                {/* Taxa de Acerto */}
                <Card className="bg-gradient-to-br from-indigo-50 to-violet-100 dark:from-indigo-900/20 dark:to-violet-900/10 border-indigo-200 dark:border-violet-800">
                    <CardHeader className="pb-2">
                        <CardTitle className="flex items-center space-x-2 text-sm font-medium text-indigo-700 dark:text-indigo-300">
                            <TrendingUp className="h-4 w-4" />
                            <span>Taxa de Acerto</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-indigo-900 dark:text-indigo-100">
                            {data.taxa_acerto_pct.toFixed(1)}%
                        </div>
                        <p className="text-xs text-indigo-700 dark:text-indigo-300 mt-1">
                            sem necessidade de correção
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Fases com Mais Erros */}
            {data.correcoes_por_fase_original && data.correcoes_por_fase_original.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">Fases com Mais Erros</CardTitle>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            Fases classificadas incorretamente mais frequentemente
                        </p>
                    </CardHeader>
                    <CardContent>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b border-gray-200 dark:border-gray-700">
                                        <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                                            Fase Original
                                        </th>
                                        <th className="text-right py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                                            Erros
                                        </th>
                                        <th className="text-right py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                                            % do Total
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                                    {data.correcoes_por_fase_original.map((row, idx) => {
                                        const percentage =
                                            data.total_corrigidos > 0
                                                ? ((row.total / data.total_corrigidos) * 100).toFixed(1)
                                                : '0.0';
                                        return (
                                            <tr
                                                key={idx}
                                                className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                                            >
                                                <td className="py-3 px-4">
                                                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getPhaseColorClasses(row.fase)}`}>
                                                        {getPhaseLabel(row.fase)}
                                                    </span>
                                                </td>
                                                <td className="py-3 px-4 text-right font-semibold text-gray-900 dark:text-white">
                                                    {row.total}
                                                </td>
                                                <td className="py-3 px-4 text-right text-gray-600 dark:text-gray-400">
                                                    {percentage}%
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Fases Corrigidas Para */}
            {data.correcoes_por_fase_corrigida && data.correcoes_por_fase_corrigida.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">Para Quais Fases Foram Corrigidas</CardTitle>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            Distribuição das fases após correção manual
                        </p>
                    </CardHeader>
                    <CardContent>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b border-gray-200 dark:border-gray-700">
                                        <th className="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                                            Fase Corrigida
                                        </th>
                                        <th className="text-right py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                                            Correções
                                        </th>
                                        <th className="text-right py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">
                                            % do Total
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                                    {data.correcoes_por_fase_corrigida.map((row, idx) => {
                                        const percentage =
                                            data.total_corrigidos > 0
                                                ? ((row.total / data.total_corrigidos) * 100).toFixed(1)
                                                : '0.0';
                                        return (
                                            <tr
                                                key={idx}
                                                className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                                            >
                                                <td className="py-3 px-4">
                                                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getPhaseColorClasses(row.fase)}`}>
                                                        {getPhaseLabel(row.fase)}
                                                    </span>
                                                </td>
                                                <td className="py-3 px-4 text-right font-semibold text-gray-900 dark:text-white">
                                                    {row.total}
                                                </td>
                                                <td className="py-3 px-4 text-right text-gray-600 dark:text-gray-400">
                                                    {percentage}%
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Empty State */}
            {(!data.correcoes_por_fase_original || data.correcoes_por_fase_original.length === 0) && (
                <Card className="bg-gray-50 dark:bg-gray-800/50 border-dashed">
                    <CardContent className="py-12">
                        <div className="text-center">
                            <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-600 dark:text-gray-400 font-medium">
                                Nenhuma correção registrada ainda
                            </p>
                            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                                As análises aparecerão aqui quando houver correções de fase registradas
                            </p>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
};

export default PhaseCorrectionAnalytics;
