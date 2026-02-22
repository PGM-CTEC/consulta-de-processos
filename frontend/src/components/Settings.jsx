import React, { useState, useEffect } from 'react';
import { Settings, Save, Loader2, Play, CheckCircle2, AlertCircle, Eye, EyeOff, Database } from 'lucide-react';
import { testSQLConnection, importFromSQL } from '../services/api';
import { toast } from 'react-hot-toast';

const SettingsComponent = () => {
    const [config, setConfig] = useState({
        driver: 'postgresql',
        host: 'localhost',
        port: 5432,
        user: '',
        password: '',
        database: '',
        query: 'SELECT numero_processo FROM processos LIMIT 100'
    });
    const [testing, setTesting] = useState(false);
    const [importing, setImporting] = useState(false);
    const [showConfig, setShowConfig] = useState(true);

    const handleConfigChange = (e) => {
        const { name, value } = e.target;
        setConfig(prev => ({
            ...prev,
            [name]: name === 'port' ? parseInt(value) || 0 : value
        }));
    };

    const handleTestConnection = async () => {
        setTesting(true);
        try {
            const result = await testSQLConnection(config);
            if (result.success) {
                toast.success(result.message);
            } else {
                toast.error(result.message);
            }
        } catch {
            toast.error('Erro ao testar conexão. Verifique os logs.');
        } finally {
            setTesting(false);
        }
    };

    const handleImport = async () => {
        if (!confirm('Deseja iniciar a importação de processos via SQL? Isso pode levar alguns minutos.')) return;
        setImporting(true);
        try {
            const result = await importFromSQL(config);
            const successCount = result.results.length;
            const failCount = result.failures.length;
            toast.success(`Importação concluída: ${successCount} sucessos, ${failCount} falhas.`);
        } catch {
            toast.error('Erro durante a importação.');
        } finally {
            setImporting(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="text-center space-y-2">
                <h2 className="text-3xl font-extrabold text-gray-900">Configurações do Sistema</h2>
                <p className="text-gray-500">Configure as integrações de dados e inteligência artificial.</p>
            </div>

            {/* SQL Extraction Configuration */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
                <div
                    className="p-4 bg-gray-50 border-b border-gray-100 flex justify-between items-center cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => setShowConfig(!showConfig)}
                >
                    <div className="flex items-center space-x-2">
                        <Database className="h-5 w-5 text-gray-500" />
                        <h3 className="font-bold text-gray-700">Extração de Dados SQL</h3>
                    </div>
                    <span className="text-gray-400 text-xs font-bold uppercase tracking-wider">
                        {showConfig ? 'Recolher' : 'Expandir'}
                    </span>
                </div>

                {showConfig && (
                    <div className="p-6 space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="space-y-1">
                                <label htmlFor="sql-driver" className="text-xs font-bold text-gray-500 uppercase tracking-wide">Driver / Banco</label>
                                <select
                                    id="sql-driver"
                                    name="driver"
                                    value={config.driver}
                                    onChange={handleConfigChange}
                                    className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                                >
                                    <option value="postgresql">PostgreSQL</option>
                                    <option value="mysql">MySQL</option>
                                    <option value="mssql+pyodbc">SQL Server (PyODBC)</option>
                                    <option value="sqlite">SQLite</option>
                                </select>
                            </div>
                            <div className="space-y-1">
                                <label htmlFor="sql-host" className="text-xs font-bold text-gray-500 uppercase tracking-wide">Host</label>
                                <input
                                    id="sql-host"
                                    type="text"
                                    name="host"
                                    value={config.host}
                                    onChange={handleConfigChange}
                                    className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2 text-sm"
                                    placeholder="localhost"
                                />
                            </div>
                            <div className="space-y-1">
                                <label htmlFor="sql-port" className="text-xs font-bold text-gray-500 uppercase tracking-wide">Porta</label>
                                <input
                                    id="sql-port"
                                    type="number"
                                    name="port"
                                    value={config.port}
                                    onChange={handleConfigChange}
                                    className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2 text-sm"
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="space-y-1">
                                <label htmlFor="sql-user" className="text-xs font-bold text-gray-500 uppercase tracking-wide">Usuário</label>
                                <input
                                    id="sql-user"
                                    type="text"
                                    name="user"
                                    value={config.user}
                                    onChange={handleConfigChange}
                                    className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2 text-sm"
                                />
                            </div>
                            <div className="space-y-1">
                                <label htmlFor="sql-password" className="text-xs font-bold text-gray-500 uppercase tracking-wide">Senha</label>
                                <input
                                    id="sql-password"
                                    type="password"
                                    name="password"
                                    value={config.password}
                                    onChange={handleConfigChange}
                                    className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2 text-sm"
                                />
                            </div>
                            <div className="space-y-1">
                                <label htmlFor="sql-database" className="text-xs font-bold text-gray-500 uppercase tracking-wide">Banco de Dados</label>
                                <input
                                    id="sql-database"
                                    type="text"
                                    name="database"
                                    value={config.database}
                                    onChange={handleConfigChange}
                                    className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2 text-sm"
                                />
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label htmlFor="sql-query" className="text-xs font-bold text-gray-500 uppercase tracking-wide">Query SQL</label>
                            <textarea
                                id="sql-query"
                                name="query"
                                value={config.query}
                                onChange={handleConfigChange}
                                rows="3"
                                className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm font-mono"
                                placeholder="SELECT cnj_number FROM processes"
                            />
                        </div>

                        <div className="flex space-x-4">
                            <button
                                onClick={handleTestConnection}
                                disabled={testing || importing}
                                className="flex-1 bg-white border-2 border-indigo-600 text-indigo-600 px-6 py-3 rounded-xl font-bold hover:bg-indigo-50 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
                            >
                                {testing ? <Loader2 className="h-5 w-5 animate-spin" /> : <CheckCircle2 className="h-5 w-5" />}
                                <span>Testar Conexão</span>
                            </button>
                            <button
                                onClick={handleImport}
                                disabled={testing || importing}
                                className="flex-1 bg-indigo-600 text-white px-6 py-3 rounded-xl font-bold shadow-lg shadow-indigo-100 hover:bg-indigo-700 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
                            >
                                {importing ? <Loader2 className="h-5 w-5 animate-spin" /> : <Play className="h-5 w-5" />}
                                <span>Iniciar Importação</span>
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SettingsComponent;
