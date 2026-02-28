import React, { useState } from 'react';
import { Loader2, Play, CheckCircle2, Database } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { standardSchemaResolver } from '@hookform/resolvers/standard-schema';
import { testSQLConnection, importFromSQL } from '../services/api';
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
