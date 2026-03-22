import React from 'react';
import { BookOpen, Info } from 'lucide-react';
import { STAGES, SUBSTAGES, TRANSIT_OPTIONS, getSubstagesForStage } from '../constants/phases';
import { getStageColorClasses } from '../utils/phaseColors';

/**
 * Componente de referência para a classificação hierárquica de fases processuais
 */
const PhaseReference = () => {

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-violet-600 rounded-2xl p-8 text-white">
        <div className="flex items-center mb-4">
          <BookOpen className="h-8 w-8 mr-3" />
          <h1 className="text-3xl font-bold">Referência de Classificação Processual</h1>
        </div>
        <p className="text-indigo-100 text-lg">
          Modelo Hierárquico PGM-Rio — Estágio / Subfase / Trânsito em Julgado
        </p>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-lg">
        <div className="flex items-start">
          <Info className="h-6 w-6 text-blue-600 mr-3 mt-0.5" />
          <div>
            <h3 className="font-bold text-blue-900 mb-2">Sobre o Sistema de Classificação</h3>
            <p className="text-blue-800 text-sm leading-relaxed">
              Este sistema implementa as 15 fases processuais definidas pela Coordenação de Tecnologia da
              Procuradoria-Geral do Município do Rio de Janeiro, baseado nas Tabelas Processuais Unificadas
              do CNJ (Resoluções 46/2007 e 326/2020) e no Modelo Nacional de Interoperabilidade (Resolução CNJ 455/2022).
            </p>
          </div>
        </div>
      </div>

      {/* Classificação Hierárquica */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="bg-gradient-to-r from-teal-50 to-cyan-50 border-b border-gray-100 px-6 py-4">
          <h2 className="text-lg font-bold text-gray-900">Classificação Hierárquica (3 Campos)</h2>
          <p className="text-sm text-gray-600 mt-1">
            Sistema alternativo que separa a classificação em Estágio, Subfase e Trânsito em Julgado
          </p>
        </div>
        <div className="p-6 space-y-6">
          {/* Stages */}
          {Object.values(STAGES).map((stage) => {
            const substages = getSubstagesForStage(stage.value);
            return (
              <div key={stage.value} className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-bold ${getStageColorClasses(stage.value)}`}>
                    {stage.value}. {stage.label}
                  </span>
                </div>
                {substages.length > 0 && (
                  <div className="ml-6 space-y-1">
                    {substages.map((ss) => (
                      <div key={ss.value} className="flex items-center gap-2 text-sm text-gray-700">
                        <span className="font-mono text-xs text-gray-400 w-8">{ss.value}</span>
                        <span>{ss.label}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}

          {/* Transit */}
          <div className="border-t border-gray-200 pt-4">
            <h3 className="text-sm font-bold text-gray-900 mb-2">Trânsito em Julgado (campo independente)</h3>
            <div className="flex gap-3">
              {Object.values(TRANSIT_OPTIONS).map((t) => (
                <span key={t.value} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-700 border border-gray-200">
                  {t.value} = {t.label}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Documentation Link */}
      <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-6 text-center border border-gray-200">
        <p className="text-sm text-gray-700">
          Para mais informações, consulte a documentação completa em{' '}
          <code className="bg-gray-200 px-2 py-0.5 rounded text-xs font-mono">
            frontend/src/constants/README-FASES.md
          </code>
        </p>
      </div>
    </div>
  );
};

export default PhaseReference;
