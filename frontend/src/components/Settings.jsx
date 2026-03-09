import React, { useState, useEffect, useCallback } from 'react';
import { Loader2, Play, CheckCircle2, Database, Globe, RefreshCw, BookmarkIcon, AlertTriangle, Wifi, WifiOff } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { standardSchemaResolver } from '@hookform/resolvers/standard-schema';
import { testSQLConnection, importFromSQL, testFusionConnection, getFusionStatus, updateFusionCookie } from '../services/api';
import { toast } from 'react-hot-toast';
import { sqlConfigSchema } from '../lib/validationSchemas';

const fieldClass = 'w-full bg-gray-50 border border-gray-200 rounded-lg p-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none';
const errorClass = 'text-red-500 text-xs mt-1';

const FieldError = ({ error }) =>
    error ? <p className={errorClass}>{error.message}</p> : null;

const SettingsComponent = () => {
    const [testing, setTesting] = useState(false);
    const [importing, setImporting] = useState(false);
    const [showConfig, setShowConfig] = useState(true);
    const [fusionCookie, setFusionCookie] = useState('');
    const [testingFusion, setTestingFusion] = useState(false);
    const [fusionResult, setFusionResult] = useState(null);
    const [fusionTestCnj, setFusionTestCnj] = useState('');
    const [fusionStatus, setFusionStatus] = useState(null);
    const [loadingStatus, setLoadingStatus] = useState(false);
    const [updatingCookie, setUpdatingCookie] = useState(false);

    const backendOrigin = import.meta.env.VITE_API_URL?.replace('/api', '') || 'http://localhost:8000';

    const bookmarkletCode = `javascript:(function(){var c=document.cookie.split(';').find(function(s){return s.trim().startsWith('JSESSIONID=')});if(!c){alert('JSESSIONID não encontrado. Verifique se você está logado no PAV.');return;}fetch('${backendOrigin}/fusion/cookie',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({cookie:c.trim()})}).then(function(r){return r.json()}).then(function(d){alert(d.success?'✓ '+d.message:'✗ '+d.message)}).catch(function(){alert('✗ Backend não encontrado em ${backendOrigin}');});})();`;

    const loadFusionStatus = useCallback(async () => {
        setLoadingStatus(true);
        try {
            const data = await getFusionStatus();
            setFusionStatus(data);
        } catch {
            setFusionStatus({ configured: false, alive: false, message: 'Erro ao verificar status.' });
        } finally {
            setLoadingStatus(false);
        }
    }, []);

    useEffect(() => { loadFusionStatus(); }, [loadFusionStatus]);

    const handleUpdateCookie = async () => {
        if (!fusionCookie.trim()) {
            toast.error('Cole o cookie JSESSIONID antes de atualizar.');
            return;
        }
        setUpdatingCookie(true);
        try {
            const result = await updateFusionCookie(fusionCookie.trim());
            if (result.success) {
                toast.success(result.message);
                setFusionCookie('');
                await loadFusionStatus();
            } else {
                toast.error(result.message);
            }
        } catch {
            toast.error('Erro ao atualizar cookie.');
        } finally {
            setUpdatingCookie(false);
        }
    };

    const {
        register,
        getValues,
        formState: { errors },
    } = useForm({
        resolver: standardSchemaResolver(sqlConfigSchema),
        mode: 'onBlur',
        defaultValues: {
            driver: 'postgresql',
            host: 'localhost',
            port: 5432,
            user: '',
            password: '',
            database: '',
            query: 'SELECT numero_processo FROM processos LIMIT 100',
        },
    });

    const handleTestConnection = async () => {
        setTesting(true);
        try {
            const result = await testSQLConnection(getValues());
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

    const handleTestFusion = async () => {
        if (!fusionTestCnj.trim()) {
            toast.error('Informe um número CNJ para testar.');
            return;
        }
        setTestingFusion(true);
        setFusionResult(null);
        try {
            const result = await testFusionConnection(fusionTestCnj.trim());
            setFusionResult(result);
            if (result.success) {
                toast.success(result.message);
            } else {
                toast.error(result.message);
            }
        } catch {
            toast.error('Erro ao testar conexão com Fusion/PAV.');
        } finally {
            setTestingFusion(false);
        }
    };

    const handleImport = async () => {
        if (!confirm('Deseja iniciar a importação de processos via SQL? Isso pode levar alguns minutos.')) return;
        setImporting(true);
        try {
            const result = await importFromSQL(getValues());
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

            {/* Fusion/PAV Integration */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
                <div className="p-4 bg-amber-50 border-b border-amber-100 flex items-center space-x-2">
                    <Globe className="h-5 w-5 text-amber-600" />
                    <h3 className="font-bold text-amber-800">Integração Fusion/PAV</h3>
                    <span className="ml-auto px-2 py-0.5 text-xs font-medium rounded-full bg-amber-100 text-amber-700 border border-amber-300">Fallback DataJud</span>
                </div>
                <div className="p-6 space-y-5">

                    {/* Status da sessão */}
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            {loadingStatus ? (
                                <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
                            ) : fusionStatus?.alive ? (
                                <Wifi className="h-4 w-4 text-green-500" />
                            ) : (
                                <WifiOff className="h-4 w-4 text-red-400" />
                            )}
                            <span className={`text-sm font-medium ${fusionStatus?.alive ? 'text-green-700' : 'text-red-600'}`}>
                                {loadingStatus ? 'Verificando…' : (fusionStatus?.message ?? 'Status desconhecido')}
                            </span>
                            {fusionStatus?.cookie_preview && (
                                <code className="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">{fusionStatus.cookie_preview}</code>
                            )}
                        </div>
                        <button
                            type="button"
                            onClick={loadFusionStatus}
                            disabled={loadingStatus}
                            className="p-1.5 text-gray-400 hover:text-amber-600 transition-colors rounded"
                            title="Verificar novamente"
                        >
                            <RefreshCw className={`h-4 w-4 ${loadingStatus ? 'animate-spin' : ''}`} />
                        </button>
                    </div>

                    {/* Aviso quando sessão expirada */}
                    {fusionStatus && !fusionStatus.alive && (
                        <div className="flex items-start gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800">
                            <AlertTriangle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                            <span>Sessão PAV expirada. Use o bookmarklet abaixo estando logado no PAV, ou cole o cookie manualmente.</span>
                        </div>
                    )}

                    {/* Bookmarklet */}
                    <div className="space-y-2">
                        <p className="text-xs font-bold text-gray-500 uppercase tracking-wide flex items-center gap-1">
                            <BookmarkIcon className="h-3.5 w-3.5" />
                            Atualização automática via Bookmarklet
                        </p>
                        <p className="text-xs text-gray-500">
                            Arraste o botão abaixo para a barra de favoritos do Chrome. Quando precisar renovar a sessão,
                            abra o PAV, clique no favorito — o cookie é enviado automaticamente para o backend.
                        </p>
                        <a
                            href={bookmarkletCode}
                            draggable="true"
                            onClick={(e) => e.preventDefault()}
                            className="inline-flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-bold rounded-lg cursor-grab active:cursor-grabbing select-none transition-colors"
                            title="Arraste para a barra de favoritos"
                        >
                            <BookmarkIcon className="h-4 w-4" />
                            Renovar Sessão PAV
                        </a>
                        <p className="text-xs text-gray-400">↑ Arraste este botão para a barra de favoritos. Não clique aqui.</p>
                    </div>

                    <hr className="border-gray-100" />

                    {/* Atualização manual */}
                    <div className="space-y-2">
                        <p className="text-xs font-bold text-gray-500 uppercase tracking-wide">Atualização manual do cookie</p>
                        <p className="text-xs text-gray-400">
                            Abra o PAV no Chrome → F12 → Application → Cookies → copie o valor de <code className="bg-gray-100 px-1 rounded">JSESSIONID</code>.
                        </p>
                        <div className="flex gap-2">
                            <input
                                id="fusion-cookie"
                                type="password"
                                value={fusionCookie}
                                onChange={(e) => setFusionCookie(e.target.value)}
                                onPaste={(e) => {
                                    const pasted = e.clipboardData.getData('text');
                                    if (pasted && !pasted.includes('JSESSIONID')) {
                                        setFusionCookie('JSESSIONID=' + pasted.trim());
                                        e.preventDefault();
                                    }
                                }}
                                className={`${fieldClass} flex-1`}
                                placeholder="JSESSIONID=ABC123… (ou só o valor)"
                            />
                            <button
                                type="button"
                                onClick={handleUpdateCookie}
                                disabled={updatingCookie || !fusionCookie.trim()}
                                className="bg-amber-500 text-white px-4 py-2 rounded-lg font-bold hover:bg-amber-600 transition-all flex items-center gap-1.5 disabled:opacity-50 whitespace-nowrap"
                            >
                                {updatingCookie ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                                Atualizar
                            </button>
                        </div>
                    </div>

                    <hr className="border-gray-100" />

                    {/* Teste de conexão */}
                    <div className="space-y-2">
                        <p className="text-xs font-bold text-gray-500 uppercase tracking-wide">Testar conexão com número CNJ</p>
                        <div className="flex gap-2">
                            <input
                                id="fusion-cnj"
                                type="text"
                                value={fusionTestCnj}
                                onChange={(e) => setFusionTestCnj(e.target.value)}
                                className={`${fieldClass} flex-1`}
                                placeholder="0000000-00.0000.8.19.0000"
                            />
                            <button
                                type="button"
                                onClick={handleTestFusion}
                                disabled={testingFusion}
                                className="bg-amber-500 text-white px-4 py-2 rounded-lg font-bold hover:bg-amber-600 transition-all flex items-center gap-1.5 disabled:opacity-50"
                            >
                                {testingFusion ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                                <span>Testar</span>
                            </button>
                        </div>
                        {fusionResult && (
                            <div className={`p-3 rounded-lg border text-sm ${fusionResult.success ? 'bg-green-50 border-green-200 text-green-800' : 'bg-red-50 border-red-200 text-red-800'}`}>
                                <p className="font-bold">{fusionResult.success ? '✓ Encontrado' : '✗ Não encontrado'}</p>
                                <p>{fusionResult.message}</p>
                                {fusionResult.success && (
                                    <ul className="mt-2 space-y-0.5 text-xs">
                                        <li><span className="font-medium">Fonte:</span> {fusionResult.fonte}</li>
                                        <li><span className="font-medium">Classe:</span> {fusionResult.classe_processual}</li>
                                        <li><span className="font-medium">Sistema:</span> {fusionResult.sistema}</li>
                                        <li><span className="font-medium">Movimentos:</span> {fusionResult.total_movimentos}</li>
                                    </ul>
                                )}
                            </div>
                        )}
                    </div>
                </div>
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
                    <form className="p-6 space-y-6" onSubmit={(e) => e.preventDefault()}>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="space-y-1">
                                <label htmlFor="sql-driver" className="text-xs font-bold text-gray-500 uppercase tracking-wide">Driver / Banco</label>
                                <select
                                    id="sql-driver"
                                    {...register('driver')}
                                    className={fieldClass}
                                >
                                    <option value="postgresql">PostgreSQL</option>
                                    <option value="mysql">MySQL</option>
                                    <option value="mssql+pyodbc">SQL Server (PyODBC)</option>
                                    <option value="sqlite">SQLite</option>
                                </select>
                                <FieldError error={errors.driver} />
                            </div>
                            <div className="space-y-1">
                                <label htmlFor="sql-host" className="text-xs font-bold text-gray-500 uppercase tracking-wide">Host</label>
                                <input
                                    id="sql-host"
                                    type="text"
                                    {...register('host')}
                                    className={fieldClass}
                                    placeholder="localhost"
                                />
                                <FieldError error={errors.host} />
                            </div>
                            <div className="space-y-1">
                                <label htmlFor="sql-port" className="text-xs font-bold text-gray-500 uppercase tracking-wide">Porta</label>
                                <input
                                    id="sql-port"
                                    type="number"
                                    {...register('port')}
                                    className={fieldClass}
                                />
                                <FieldError error={errors.port} />
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="space-y-1">
                                <label htmlFor="sql-user" className="text-xs font-bold text-gray-500 uppercase tracking-wide">Usuário</label>
                                <input
                                    id="sql-user"
                                    type="text"
                                    {...register('user')}
                                    className={fieldClass}
                                />
                            </div>
                            <div className="space-y-1">
                                <label htmlFor="sql-password" className="text-xs font-bold text-gray-500 uppercase tracking-wide">Senha</label>
                                <input
                                    id="sql-password"
                                    type="password"
                                    {...register('password')}
                                    className={fieldClass}
                                />
                            </div>
                            <div className="space-y-1">
                                <label htmlFor="sql-database" className="text-xs font-bold text-gray-500 uppercase tracking-wide">Banco de Dados</label>
                                <input
                                    id="sql-database"
                                    type="text"
                                    {...register('database')}
                                    className={fieldClass}
                                />
                                <FieldError error={errors.database} />
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label htmlFor="sql-query" className="text-xs font-bold text-gray-500 uppercase tracking-wide">Query SQL</label>
                            <textarea
                                id="sql-query"
                                {...register('query')}
                                rows="3"
                                className={`${fieldClass} font-mono`}
                                placeholder="SELECT cnj_number FROM processes"
                            />
                            <FieldError error={errors.query} />
                        </div>

                        <div className="flex space-x-4">
                            <button
                                type="button"
                                onClick={handleTestConnection}
                                disabled={testing || importing}
                                className="flex-1 bg-white border-2 border-indigo-600 text-indigo-600 px-6 py-3 rounded-xl font-bold hover:bg-indigo-50 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
                            >
                                {testing ? <Loader2 className="h-5 w-5 animate-spin" /> : <CheckCircle2 className="h-5 w-5" />}
                                <span>Testar Conexão</span>
                            </button>
                            <button
                                type="button"
                                onClick={handleImport}
                                disabled={testing || importing}
                                className="flex-1 bg-indigo-600 text-white px-6 py-3 rounded-xl font-bold shadow-lg shadow-indigo-100 hover:bg-indigo-700 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
                            >
                                {importing ? <Loader2 className="h-5 w-5 animate-spin" /> : <Play className="h-5 w-5" />}
                                <span>Iniciar Importação</span>
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
};

export default SettingsComponent;
