import React, { useState } from 'react';
import { Upload, Search, FileText, CheckCircle, XCircle, Loader2, Download, ChevronDown } from 'lucide-react';
import { bulkSearch } from '../services/api';
import * as XLSX from 'xlsx';

const BulkSearch = () => {
    const [numbers, setNumbers] = useState('');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [showExportMenu, setShowExportMenu] = useState(false);

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

    const getExportData = () => {
        if (!results) return [];
        return results.results.map(p => ({
            'Número': p.number,
            'Tribunal': p.tribunal_name || p.court?.split(' - ')[0] || 'N/A',
            'Sede / Vara': p.court_unit || p.court?.split(' - ')[1] || p.court || 'N/A',
            'Fase Atual': p.phase || 'Conhecimento'
        }));
    };

    const exportToCSV = () => {
        const data = getExportData();
        const headers = ['Número', 'Tribunal', 'Sede / Vara', 'Fase Atual'];
        const csvContent = [
            headers.join(','),
            ...data.map(row => Object.values(row).map(v => `"${v}"`).join(','))
        ].join('\n');
        downloadFile(csvContent, 'csv', 'text/csv');
    };

    const exportToXLSX = () => {
        const data = getExportData();
        const worksheet = XLSX.utils.json_to_sheet(data);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Processos');
        XLSX.writeFile(workbook, `consulta_lote_${new Date().getTime()}.xlsx`);
    };

    const exportToTXT = () => {
        const data = getExportData();
        const txtContent = data.map(row =>
            `${row['Número']} | ${row['Tribunal']} | ${row['Sede / Vara']} | ${row['Fase Atual']}`
        ).join('\n');
        downloadFile(txtContent, 'txt', 'text/plain');
    };

    const exportToMD = () => {
        const data = getExportData();
        const headers = ['Número', 'Tribunal', 'Sede / Vara', 'Fase Atual'];
        const mdHeader = `| ${headers.join(' | ')} |`;
        const mdDivider = `| ${headers.map(() => '---').join(' | ')} |`;
        const mdRows = data.map(row => `| ${Object.values(row).join(' | ')} |`).join('\n');
        const mdContent = `${mdHeader}\n${mdDivider}\n${mdRows}`;
        downloadFile(mdContent, 'md', 'text/markdown');
    };

    const downloadFile = (content, ext, type) => {
        const blob = new Blob([content], { type: `${type};charset=utf-8;` });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `consulta_lote_${new Date().getTime()}.${ext}`);
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
                    <div className="p-6 border-b border-gray-100 flex justify-between items-center relative">
                        <div>
                            <h3 className="text-lg font-bold text-gray-900">Resultados da Consulta</h3>
                            <p className="text-sm text-gray-500">
                                {results.results.length} processados | {results.failures.length} falhas
                            </p>
                        </div>

                        <div className="relative">
                            <button
                                onClick={() => setShowExportMenu(!showExportMenu)}
                                className="flex items-center space-x-2 bg-emerald-600 text-white px-4 py-2 rounded-lg font-bold hover:bg-emerald-700 transition-colors shadow-sm"
                            >
                                <Download className="h-5 w-5" />
                                <span>Exportar Relatório</span>
                                <ChevronDown className={`h-4 w-4 transition-transform ${showExportMenu ? 'rotate-180' : ''}`} />
                            </button>

                            {showExportMenu && (
                                <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-100 rounded-xl shadow-2xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                                    <button onClick={() => { exportToCSV(); setShowExportMenu(false); }} className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 font-medium border-b border-gray-50 flex items-center">
                                        <FileText className="mr-2 h-4 w-4 text-emerald-500" /> Excel / CSV (.csv)
                                    </button>
                                    <button onClick={() => { exportToXLSX(); setShowExportMenu(false); }} className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 font-medium border-b border-gray-50 flex items-center">
                                        <FileText className="mr-2 h-4 w-4 text-green-600" /> Planilha Excel (.xlsx)
                                    </button>
                                    <button onClick={() => { exportToTXT(); setShowExportMenu(false); }} className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 font-medium border-b border-gray-50 flex items-center">
                                        <FileText className="mr-2 h-4 w-4 text-gray-600" /> Texto Puro (.txt)
                                    </button>
                                    <button onClick={() => { exportToMD(); setShowExportMenu(false); }} className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 font-medium flex items-center">
                                        <FileText className="mr-2 h-4 w-4 text-blue-600" /> Markdown (.md)
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead className="bg-gray-50 border-b border-gray-100">
                                <tr>
                                    <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Processo Judicial</th>
                                    <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Tribunal</th>
                                    <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Órgão Judicial / Vara</th>
                                    <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Fase Atual</th>
                                    <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {results.results.map((p, idx) => (
                                    <tr key={idx} className="hover:bg-gray-50/50 transition-colors">
                                        <td className="px-6 py-4 font-mono font-bold text-gray-900 text-sm whitespace-nowrap">
                                            {p.number}
                                        </td>
                                        <td className="px-6 py-4 text-sm font-semibold text-indigo-600">
                                            {p.tribunal_name || p.court?.split(' - ')[0] || 'N/A'}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-600">
                                            {p.court_unit || p.court?.split(' - ')[1] || p.court || 'N/A'}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider ${p.phase === 'Fase Executiva' ? 'bg-orange-100 text-orange-800' :
                                                    p.phase === 'Trânsito em Julgado' ? 'bg-green-100 text-green-800' :
                                                        'bg-blue-100 text-blue-800'
                                                }`}>
                                                {p.phase || 'Conhecimento'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center text-green-600 text-xs font-semibold">
                                                <CheckCircle className="h-4 w-4 mr-1" /> OK
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                                {results.failures.map((num, idx) => (
                                    <tr key={`fail-${idx}`} className="bg-red-50/20">
                                        <td className="px-6 py-4 font-mono text-sm text-red-700 font-bold">{num}</td>
                                        <td colSpan="3" className="px-6 py-4 text-xs text-red-500 italic font-medium">
                                            Não localizado nos sistemas DataJud
                                        </td>
                                        <td className="px-6 py-4">
                                            <XCircle className="h-4 w-4 text-red-500" />
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
