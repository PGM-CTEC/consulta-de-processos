import React from 'react';
import PropTypes from 'prop-types';
import { Calendar, Building2, Gavel, FileText } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { getPhaseColorClasses, getPhaseDisplayName } from '../utils/phaseColors';

function ProcessDetails({ data }) {
    if (!data) return null;

    return (
        <article className="max-w-4xl mx-auto p-4 space-y-6" aria-labelledby="process-title">
            {/* Header Card */}
            <section className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden" aria-label="Informações do processo">
                <header className="bg-gradient-to-r from-indigo-600 to-violet-600 p-6 text-white">
                    <h1 id="process-title" className="text-2xl font-bold font-mono tracking-wide">{data.number}</h1>
                    <p className="opacity-90 mt-1">{data.subject || 'Assunto não informado'}</p>
                </header>
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
                        <FileText className="h-5 w-5 text-violet-500 mt-1" aria-hidden="true" />
                        <div>
                            <p className="text-xs text-gray-500 uppercase font-semibold">Fase Atual</p>
                            <div className="mt-1">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPhaseColorClasses(data.phase)}`}>
                                    {getPhaseDisplayName(data.phase)}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Timeline */}
            <section className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6" aria-labelledby="movements-heading">
                <h2 id="movements-heading" className="text-lg font-bold text-gray-900 mb-6 flex items-center">
                    <FileText className="mr-2 h-5 w-5 text-indigo-600" aria-hidden="true" />
                    Movimentações
                </h2>

                <ol className="relative border-l-2 border-indigo-100 ml-3 space-y-8 pl-8 pb-4 list-none">
                    {data.movements?.map((mov, idx) => (
                        <li key={mov.id || idx} className="relative">
                            <span className="absolute -left-[41px] top-1 h-5 w-5 rounded-full border-4 border-white bg-indigo-500 shadow-sm" aria-hidden="true" />
                            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start">
                                <div>
                                    <p className="text-base font-medium text-gray-900">{mov.description}</p>
                                    <p className="text-sm text-gray-500 mt-1">Código: {mov.code || 'S/N'}</p>
                                </div>
                                <time
                                    dateTime={mov.date}
                                    className="text-xs font-mono text-gray-400 whitespace-nowrap bg-gray-50 px-2 py-1 rounded mt-2 sm:mt-0"
                                >
                                    {format(new Date(mov.date), "dd MMM yyyy, HH:mm", { locale: ptBR })}
                                </time>
                            </div>
                        </li>
                    ))}
                    {data.movements?.length === 0 && (
                        <li className="text-gray-500 italic">Nenhuma movimentação registrada.</li>
                    )}
                </ol>
            </section>
        </article>
    );
}

ProcessDetails.propTypes = {
    data: PropTypes.shape({
        number: PropTypes.string.isRequired,
        subject: PropTypes.string,
        class_nature: PropTypes.string,
        court: PropTypes.string,
        distribution_date: PropTypes.string,
        phase: PropTypes.string,
        movements: PropTypes.arrayOf(
            PropTypes.shape({
                id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
                description: PropTypes.string.isRequired,
                code: PropTypes.string,
                date: PropTypes.string.isRequired,
            })
        ),
    }),
};

export default ProcessDetails;
