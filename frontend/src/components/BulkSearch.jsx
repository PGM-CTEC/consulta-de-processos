import React, { useState, useRef } from 'react';
import { Upload, Search, FileText, CheckCircle, XCircle, Loader2, Download, ChevronDown, FileUp, AlertCircle } from 'lucide-react';
import { LoadingState } from './LoadingState';
import { bulkSearch } from '../services/api';
import * as XLSX from 'xlsx';
import { getPhaseColorClasses, getPhaseDisplayName } from '../utils/phaseColors';
import { exporters } from '../utils/exportHelpers';

const BulkSearch = () => {
    const [numbers, setNumbers] = useState('');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [showExportMenu, setShowExportMenu] = useState(false);
    const [dragging, setDragging] = useState(false);
    const fileInputRef = useRef(null);

    const handleSearch = async () => {
        const processList = numbers.split('\n').map(n => n.trim()).filter(n => n.length > 0);
        if (processList.length === 0) return;

        setLoading(true);
        setError(null);
        try {
            const data = await bulkSearch(processList);
            setResults(data);
        } catch {
            setError('Falha ao processar a busca em lote.');
        } finally {
            setLoading(false);
        }
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) parseFile(file);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setDragging(true);
    };

    const handleDragLeave = () => {
        setDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files[0];
        if (file) parseFile(file);
    };

    const parseFile = (file) => {
        const reader = new FileReader();
        const extension = file.name.split('.').pop().toLowerCase();

        reader.onload = (e) => {
            const content = e.target.result;
            let detectedNumbers = [];

            try {
                if (extension === 'txt') {
                    detectedNumbers = content.split('\n').map(n => n.trim()).filter(n => n.length > 0);
                } else if (extension === 'csv' || extension === 'xlsx') {
                    const workbook = XLSX.read(content, { type: 'binary' });
                    const firstSheetName = workbook.SheetNames[0];
                    const worksheet = workbook.Sheets[firstSheetName];
                    const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

                    // Extract from first column of each row
                    detectedNumbers = jsonData.map(row => row[0]?.toString().trim()).filter(n => n && n.length > 0);
                }

                if (detectedNumbers.length > 0) {
                    setNumbers(detectedNumbers.join('\n'));
                    setError(null);
                } else {
                    setError('Nenhum número de processo detectado no arquivo.');
                }
            } catch {
                setError('Erro ao ler o arquivo. Verifique o formato.');
            }
        };

        if (extension === 'txt') {
            reader.readAsText(file);
        } else {
            reader.readAsBinaryString(file);
        }
    };

    // Export functions now use centralized utilities
    const handleExportCSV = () => exporters.csv(results.results);
    const handleExportXLSX = () => exporters.xlsx(results.results);
    const handleExportTXT = () => exporters.txt(results.results);
    const handleExportMD = () => exporters.md(results.results);

    return (
        <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
                <div className="p-6 bg-gradient-to-r from-violet-600 to-indigo-600">
                    <h2 className="text-xl font-bold text-white flex items-center">
                        <Upload className="mr-2 h-6 w-6" />
                        Busca em Lote (Milhares de Processos)
                    </h2>
                    <p className="text-violet-100 text-sm mt-1">
                        Insira os números abaixo ou faça o upload de um arquivo.
                    </p>
                </div>

                <div className="p-6 space-y-4">
                    {/* Drag and Drop Zone */}
                    <div
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        onClick={() => fileInputRef.current.click()}
                        className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all ${dragging ? 'border-violet-500 bg-violet-50' : 'border-gray-200 hover:border-violet-300 hover:bg-gray-50'
                            }`}
                    >
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileChange}
                            accept=".txt,.csv,.xlsx"
                            className="hidden"
                        />
                        <FileUp className={`h-10 w-10 mb-3 ${dragging ? 'text-violet-500' : 'text-gray-400'}`} />
                        <p className="text-sm font-semibold text-gray-700">Clique ou arraste um arquivo para importar</p>
                        <p className="text-xs text-gray-600 mt-1">Suporta .txt, .csv e .xlsx</p>
                    </div>

                    <div className="relative">
                        <label
                            htmlFor="bulk-numbers-textarea"
                            className="absolute top-3 left-4 flex items-center text-xs font-bold text-gray-600 uppercase tracking-widest bg-white pr-2"
                        >
                            Listagem de Números
                        </label>
                        <textarea
                            id="bulk-numbers-textarea"
                            className="w-full h-48 p-6 pt-10 border rounded-xl focus:ring-2 focus:ring-violet-500 focus:border-transparent font-mono text-sm leading-relaxed"
                            placeholder="Um número por linha..."
                            value={numbers}
                            onChange={(e) => setNumbers(e.target.value)}
                        />
                    </div>

                    <button
                        onClick={handleSearch}
                        disabled={loading || !numbers.trim()}
                        className={`w-full flex items-center justify-center p-4 rounded-xl font-bold text-white transition-all ${loading ? 'bg-gray-400' : 'bg-violet-600 hover:bg-violet-700 shadow-lg shadow-violet-200'
                            }`}
                    >
                        {loading ? (
                            <Loader2 className="animate-spin mr-2 h-5 w-5" />
                        ) : (
                            <Search className="mr-2 h-5 w-5" />
                        )}
                        {loading ? 'Processando Lote...' : 'Iniciar Consulta em Lote'}
                    </button>
                    {error && (
                        <div className="flex items-center text-red-500 bg-red-50 p-3 rounded-lg text-sm font-medium">
                            <AlertCircle className="h-4 w-4 mr-2" />
                            {error}
                        </div>
                    )}
                </div>
            </div>

            {results && (
                <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
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
                                    <button onClick={() => { handleExportCSV(); setShowExportMenu(false); }} className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 font-medium border-b border-gray-50 flex items-center">
                                        <FileText className="mr-2 h-4 w-4 text-emerald-500" aria-hidden="true" /> Excel / CSV (.csv)
                                    </button>
                                    <button onClick={() => { handleExportXLSX(); setShowExportMenu(false); }} className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 font-medium border-b border-gray-50 flex items-center">
                                        <FileText className="mr-2 h-4 w-4 text-green-600" aria-hidden="true" /> Planilha Excel (.xlsx)
                                    </button>
                                    <button onClick={() => { handleExportTXT(); setShowExportMenu(false); }} className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 font-medium border-b border-gray-50 flex items-center">
                                        <FileText className="mr-2 h-4 w-4 text-gray-600" aria-hidden="true" /> Texto Puro (.txt)
                                    </button>
                                    <button onClick={() => { handleExportMD(); setShowExportMenu(false); }} className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 font-medium flex items-center">
                                        <FileText className="mr-2 h-4 w-4 text-blue-600" aria-hidden="true" /> Markdown (.md)
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead className="bg-gray-50 border-b border-gray-100">
                                <tr>
                                    <th className="px-6 py-4 text-xs font-bold text-gray-600 uppercase tracking-widest">Processo Judicial</th>
                                    <th className="px-6 py-4 text-xs font-bold text-gray-600 uppercase tracking-widest">Tribunal</th>
                                    <th className="px-6 py-4 text-xs font-bold text-gray-600 uppercase tracking-widest">Órgão Judicial / Vara</th>
                                    <th className="px-6 py-4 text-xs font-bold text-gray-600 uppercase tracking-widest">Fase Atual</th>
                                    <th className="px-6 py-4 text-xs font-bold text-gray-600 uppercase tracking-widest">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {results.results.map((p) => (
                                    <tr key={p.number} className="hover:bg-gray-50/50 transition-colors">
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
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider ${getPhaseColorClasses(p.phase, p.class_nature)}`}>
                                                {getPhaseDisplayName(p.phase, p.class_nature)}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center text-green-600 text-xs font-semibold">
                                                <CheckCircle className="h-4 w-4 mr-1" /> OK
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                                {results.failures.map((num) => (
                                    <tr key={`failure-${num}`} className="bg-red-50/20">
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
