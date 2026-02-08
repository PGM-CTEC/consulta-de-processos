import React from 'react';
import { BookOpen, Info } from 'lucide-react';
import { ALL_PHASES } from '../constants/phases';
import { getPhaseColorClasses, getPhaseIcon } from '../utils/phaseColors';

/**
 * Componente de referência que exibe as 15 fases processuais oficiais
 * Útil para documentação, validação e treinamento de usuários
 */
const PhaseReference = () => {
  // Agrupar fases por tipo
  const phasesByType = ALL_PHASES.reduce((acc, phase) => {
    if (!acc[phase.type]) {
      acc[phase.type] = [];
    }
    acc[phase.type].push(phase);
    return acc;
  }, {});

  const typeInfo = {
    'Conhecimento': {
      description: 'Fases relacionadas ao processo de conhecimento, divididas por instância',
      icon: '📋'
    },
    'Execução': {
      description: 'Fases de execução ou cumprimento de sentença',
      icon: '⚖️'
    },
    'Transversal': {
      description: 'Fase que pode ocorrer tanto em conhecimento quanto em execução',
      icon: '⏸️'
    },
    'Final': {
      description: 'Fase terminal indicando encerramento definitivo do processo',
      icon: '📦'
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-violet-600 rounded-2xl p-8 text-white">
        <div className="flex items-center mb-4">
          <BookOpen className="h-8 w-8 mr-3" />
          <h1 className="text-3xl font-bold">Referência de Fases Processuais</h1>
        </div>
        <p className="text-indigo-100 text-lg">
          Modelo de Classificação PGM-Rio — 15 Fases Oficiais (Versão 2.0 — Fevereiro 2026)
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

      {/* Fases agrupadas por tipo */}
      {Object.entries(phasesByType).map(([type, phases]) => (
        <div key={type} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="bg-gray-50 border-b border-gray-100 px-6 py-4">
            <div className="flex items-center">
              <span className="text-2xl mr-3">{typeInfo[type]?.icon}</span>
              <div>
                <h2 className="text-lg font-bold text-gray-900">{type}</h2>
                <p className="text-sm text-gray-600">{typeInfo[type]?.description}</p>
              </div>
            </div>
          </div>

          <div className="divide-y divide-gray-100">
            {phases.map((phase) => (
              <div key={phase.code} className="p-5 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-indigo-100 text-indigo-700 font-bold text-sm">
                        {phase.code}
                      </span>
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-bold ${getPhaseColorClasses(phase.name)}`}>
                        {phase.name}
                      </span>
                    </div>
                  </div>
                  <span className="text-2xl ml-4">{getPhaseIcon(phase.name)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Color Legend */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Legenda de Cores</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-blue-100 border-2 border-blue-200"></div>
            <div>
              <p className="font-semibold text-gray-900 text-sm">Azul</p>
              <p className="text-xs text-gray-600">Conhecimento em andamento</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-green-100 border-2 border-green-200"></div>
            <div>
              <p className="font-semibold text-gray-900 text-sm">Verde</p>
              <p className="text-xs text-gray-600">Trânsito em julgado</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-orange-100 border-2 border-orange-200"></div>
            <div>
              <p className="font-semibold text-gray-900 text-sm">Laranja</p>
              <p className="text-xs text-gray-600">Execução</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-yellow-100 border-2 border-yellow-200"></div>
            <div>
              <p className="font-semibold text-gray-900 text-sm">Amarelo</p>
              <p className="text-xs text-gray-600">Suspenso/Sobrestado</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-purple-100 border-2 border-purple-200"></div>
            <div>
              <p className="font-semibold text-gray-900 text-sm">Roxo</p>
              <p className="text-xs text-gray-600">Conversão em renda</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-gray-100 border-2 border-gray-200"></div>
            <div>
              <p className="font-semibold text-gray-900 text-sm">Cinza</p>
              <p className="text-xs text-gray-600">Arquivado definitivamente</p>
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
