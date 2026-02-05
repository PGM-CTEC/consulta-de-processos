import React, { useState, useEffect } from 'react';
import { Settings, Cpu, Save, Loader2, Play, CheckCircle2, AlertCircle, Eye, EyeOff, Database } from 'lucide-react';
import { testSQLConnection, importFromSQL, getAISettings, updateAISettings } from '../services/api';
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
    const [aiConfig, setAiConfig] = useState({ api_key: '', model: 'google/gemini-2.0-flash-001' });
    const [maskedKey, setMaskedKey] = useState('');
    const [savingAi, setSavingAi] = useState(false);
    const [showKeyContent, setShowKeyContent] = useState(false);
    const [showAiConfig, setShowAiConfig] = useState(true);

    useEffect(() => {
        loadAiSettings();
    }, []);

    const loadAiSettings = async () => {
        try {
            const result = await getAISettings();
            setMaskedKey(result.masked_key);
        } catch {
            // Error already logged or handled
        }
    };

    const handleConfigChange = (e) => {
        const { name, value } = e.target;
        setConfig(prev => ({
            ...prev,
            [name]: name === 'port' ? parseInt(value) || 0 : value
        }));
    };

    const handleAiConfigChange = (e) => {
        const { name, value } = e.target;
        setAiConfig(prev => ({ ...prev, [name]: value }));
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

    const handleSaveAiConfig = async () => {
        if (!aiConfig.api_key) {
            toast.error('Informe a chave API');
            return;
        }
        setSavingAi(true);
        try {
            const result = await updateAISettings(aiConfig);
            if (result.success) {
                toast.success(result.message);
                setMaskedKey(result.masked_key);
                setAiConfig(prev => ({ ...prev, api_key: '' }));
                setShowKeyContent(false);
            }
        } catch {
            toast.error('Erro ao salvar configuração de IA');
        } finally {
            setSavingAi(false);
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
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">Driver / Banco</label>
                                <select
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
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">Host</label>
                                <input
                                    type="text"
                                    name="host"
                                    value={config.host}
                                    onChange={handleConfigChange}
                                    className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2 text-sm"
                                    placeholder="localhost"
                                />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">Porta</label>
                                <input
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
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">Usuário</label>
                                <input
                                    type="text"
                                    name="user"
                                    value={config.user}
                                    onChange={handleConfigChange}
                                    className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2 text-sm"
                                />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">Senha</label>
                                <input
                                    type="password"
                                    name="password"
                                    value={config.password}
                                    onChange={handleConfigChange}
                                    className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2 text-sm"
                                />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">Banco de Dados</label>
                                <input
                                    type="text"
                                    name="database"
                                    value={config.database}
                                    onChange={handleConfigChange}
                                    className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2 text-sm"
                                />
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">Query SQL</label>
                            <textarea
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

            {/* AI Integration Configuration */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
                <div
                    className="p-4 bg-indigo-50 border-b border-indigo-100 flex justify-between items-center cursor-pointer hover:bg-indigo-100 transition-colors"
                    onClick={() => setShowAiConfig(!showAiConfig)}
                >
                    <div className="flex items-center space-x-2">
                        <Cpu className="h-5 w-5 text-indigo-600" />
                        <h3 className="font-bold text-indigo-700">Inteligência Artificial (OpenRouter)</h3>
                    </div>
                    <div className="flex items-center space-x-3">
                        {maskedKey && (
                            <span className="text-[10px] bg-indigo-200 text-indigo-700 px-2 py-0.5 rounded font-bold uppercase">
                                Ativa: {maskedKey}
                            </span>
                        )}
                        <span className="text-gray-400 text-xs font-bold uppercase tracking-wider">
                            {showAiConfig ? 'Recolher' : 'Expandir'}
                        </span>
                    </div>
                </div>

                {showAiConfig && (
                    <div className="p-6 space-y-6">
                        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start space-x-3">
                            <AlertCircle className="h-5 w-5 text-amber-600 mt-0.5" />
                            <p className="text-sm text-amber-800">
                                A chave API é salva de forma segura e nunca exibida integralmente.
                            </p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">OpenRouter API Key</label>
                                <div className="relative">
                                    <input
                                        type={showKeyContent ? "text" : "password"}
                                        name="api_key"
                                        value={aiConfig.api_key}
                                        onChange={handleAiConfigChange}
                                        className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm focus:ring-2 focus:ring-indigo-500 outline-none pr-12"
                                        placeholder="sk-or-v1-..."
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowKeyContent(!showKeyContent)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-indigo-600"
                                    >
                                        {showKeyContent ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                                    </button>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">Modelo de IA</label>
                                <input
                                    type="text"
                                    name="model"
                                    value={aiConfig.model}
                                    onChange={handleAiConfigChange}
                                    className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"
                                />
                            </div>
                        </div>

                        <div className="flex justify-end">
                            <button
                                onClick={handleSaveAiConfig}
                                disabled={savingAi}
                                className="bg-indigo-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-indigo-700 transition-all flex items-center space-x-2 disabled:opacity-50"
                            >
                                {savingAi ? <Loader2 className="h-5 w-5 animate-spin" /> : <Save className="h-5 w-5" />}
                                <span>Salvar Configuração</span>
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SettingsComponent;
