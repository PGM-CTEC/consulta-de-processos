import React from 'react';
import { Calendar, Building2, Gavel, FileText } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export default function ProcessDetails({ data }) {
    if (!data) return null;

    return (
        <div className="max-w-4xl mx-auto p-4 space-y-6">
            {/* Header Card */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="bg-gradient-to-r from-indigo-600 to-violet-600 p-6 text-white">
                    <h1 className="text-2xl font-bold font-mono tracking-wide">{data.number}</h1>
                    <p className="opacity-90 mt-1">{data.subject || 'Assunto não informado'}</p>
                </div>
                <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
                    <div className="flex items-start space-x-3">
                        <Gavel className="h-5 w-5 text-indigo-500 mt-1" />
                        <div>
                            <p className="text-xs text-gray-500 uppercase font-semibold">Classe</p>
                            <p className="text-sm font-medium text-gray-900 leading-tight">{data.class_nature || 'N/A'}</p>
                        </div>
                    </div>
                    <div className="flex items-start space-x-3">
                        <Building2 className="h-5 w-5 text-indigo-500 mt-1" />
                        <div>
                            <p className="text-xs text-gray-500 uppercase font-semibold">Tribunal / Vara</p>
                            <p className="text-sm font-medium text-gray-900 leading-tight">{data.court || 'N/A'}</p>
                        </div>
                    </div>
                    <div className="flex items-start space-x-3">
                        <Calendar className="h-5 w-5 text-indigo-500 mt-1" />
                        <div>
                            <p className="text-xs text-gray-500 uppercase font-semibold">Distribuição</p>
                            <p className="text-sm font-medium text-gray-900">
                                {data.distribution_date
                                    ? format(new Date(data.distribution_date), "dd/MM/yyyy", { locale: ptBR })
                                    : 'N/A'}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-start space-x-3">
                        <FileText className="h-5 w-5 text-violet-500 mt-1" />
                        <div>
                            <p className="text-xs text-gray-500 uppercase font-semibold">Fase Atual</p>
                            <div className="mt-1">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${data.phase === 'Execução' ? 'bg-orange-100 text-orange-800' :
                                        data.phase === 'Trânsito em Julgado' ? 'bg-green-100 text-green-800' :
                                            data.phase === 'Arquivado / Baixa Definitiva' ? 'bg-gray-100 text-gray-800' :
                                                'bg-blue-100 text-blue-800'
                                    }`}>
                                    {data.phase || 'Conhecimento'}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Timeline */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center">
                    <FileText className="mr-2 h-5 w-5  text-indigo-600" />
                    Movimentações
                </h2>

                <div className="relative border-l-2 border-indigo-100 ml-3 space-y-8 pl-8 pb-4">
                    {data.movements?.map((mov, idx) => (
                        <div key={mov.id || idx} className="relative">
                            <span className="absolute -left-[41px] top-1 h-5 w-5 rounded-full border-4 border-white bg-indigo-500 shadow-sm" />
                            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start">
                                <div>
                                    <p className="text-base font-medium text-gray-900">{mov.description}</p>
                                    <p className="text-sm text-gray-500 mt-1">Código: {mov.code || 'S/N'}</p>
                                </div>
                                <span className="text-xs font-mono text-gray-400 whitespace-nowrap bg-gray-50 px-2 py-1 rounded mt-2 sm:mt-0">
                                    {format(new Date(mov.date), "dd MMM yyyy, HH:mm", { locale: ptBR })}
                                </span>
                            </div>
                        </div>
                    ))}
                    {data.movements?.length === 0 && (
                        <p className="text-gray-500 italic">Nenhuma movimentação registrada.</p>
                    )}
                </div>
            </div>
        </div>
    );
}
