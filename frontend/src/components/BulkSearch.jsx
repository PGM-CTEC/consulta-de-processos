import React, { useState } from 'react';
import { Upload, Search, FileText, CheckCircle, XCircle, Loader2, Download } from 'lucide-react';
import { bulkSearch } from '../services/api';

const BulkSearch = () => {
    const [numbers, setNumbers] = useState('');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);

    const handleSearch = async () => {
        const processList = numbers.split('\n').map(n => n.trim()).filter(n => n.length > 0);
        if (processList.length === 0) return;

        setLoading(true);
        setError(null);
        try {
            const data = await bulkSearch(processList);
            setResults(data);
        } catch (err) {
            setError('Falha ao processar a busca em lote.');
        } finally {
            setLoading(false);
        }
    };

    const downloadCSV = () => {
        if (!results) return;

        const headers = ['Número', 'Classe', 'Assunto', 'Tribunal', 'Data Distribuição', 'Fase Atual'];
        const rows = results.results.map(p => [
            p.number,
            p.class_nature,
            p.subject,
            p.court,
            p.distribution_date ? new Date(p.distribution_date).toLocaleDateString('pt-BR') : 'N/A',
            p.phase
        ]);

        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.map(cell => `"${cell || ''}"`).join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `consulta_processual_lote_${new Date().getTime()}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
                <div className="p-6 bg-gradient-to-r from-violet-600 to-indigo-600">
                    <h2 className="text-xl font-bold text-white flex items-center">
                        <Upload className="mr-2 h-6 w-6" />
                        Busca em Lote (Milhares de Processos)
                    </h2>
                    <p className="text-violet-100 text-sm mt-1">
                        Insira um número por linha para realizar a consulta simultânea.
                    </p>
                </div>

                <div className="p-6">
                    <textarea
                        className="w-full h-48 p-4 border rounded-xl focus:ring-2 focus:ring-violet-500 focus:border-transparent font-mono text-sm leading-relaxed"
                        placeholder="Exemplo:&#10;0001745-93.1989.8.19.0002&#10;0002834-12.2023.8.19.0001"
                        value={numbers}
                        onChange={(e) => setNumbers(e.target.value)}
                    />

                    <button
                        onClick={handleSearch}
                        disabled={loading || !numbers.trim()}
                        className={`mt-4 w-full flex items-center justify-center p-4 rounded-xl font-bold text-white transition-all ${loading ? 'bg-gray-400' : 'bg-violet-600 hover:bg-violet-700 shadow-lg shadow-violet-200'
                            }`}
                    >
                        {loading ? (
                            <Loader2 className="animate-spin mr-2 h-5 w-5" />
                        ) : (
                            <Search className="mr-2 h-5 w-5" />
                        )}
                        {loading ? 'Processando...' : 'Pesquisar em Lote'}
                    </button>
                    {error && <p className="mt-2 text-red-500 text-sm font-medium">{error}</p>}
                </div>
            </div>

            {results && (
                <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
                    <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                        <div>
                            <h3 className="text-lg font-bold text-gray-900">Resultados</h3>
                            <p className="text-sm text-gray-500">
                                {results.results.length} processados com sucesso | {results.failures.length} falhas
                            </p>
                        </div>
                        <button
                            onClick={downloadCSV}
                            className="flex items-center space-x-2 bg-emerald-50 text-emerald-700 px-4 py-2 rounded-lg font-semibold hover:bg-emerald-100 transition-colors"
                        >
                            <Download className="h-5 w-5" />
                            <span>Exportar CSV</span>
                        </button>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-gray-50 border-b border-gray-100">
                                <tr>
                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Número</th>
                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Classe / Assunto</th>
                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Fase Atual</th>
                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Tribunal</th>
                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {results.results.map((p, idx) => (
                                    <tr key={idx} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4 font-mono text-sm">{p.number}</td>
                                        <td className="px-6 py-4">
                                            <div className="text-sm font-semibold text-gray-900">{p.class_nature}</div>
                                            <div className="text-xs text-gray-400 uppercase tracking-tight">{p.subject}</div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${p.phase === 'Fase Executiva' ? 'bg-orange-100 text-orange-800' :
                                                    p.phase === 'Trânsito em Julgado' ? 'bg-green-100 text-green-800' :
                                                        'bg-blue-100 text-blue-800'
                                                }`}>
                                                {p.phase}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-600">{p.court}</td>
                                        <td className="px-6 py-4">
                                            <CheckCircle className="h-5 w-5 text-green-500" />
                                        </td>
                                    </tr>
                                ))}
                                {results.failures.map((num, idx) => (
                                    <tr key={`fail-${idx}`} className="bg-red-50/30">
                                        <td className="px-6 py-4 font-mono text-sm text-red-700">{num}</td>
                                        <td colSpan="3" className="px-6 py-4 text-sm text-red-500 italic">Não encontrado na base pública</td>
                                        <td className="px-6 py-4">
                                            <XCircle className="h-5 w-5 text-red-500" />
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default BulkSearch;
