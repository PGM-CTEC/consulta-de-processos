import { useState, useEffect } from 'react';
import { BookOpen, ChevronDown, ChevronUp } from 'lucide-react';
import { STAGES, TRANSIT_OPTIONS, getSubstagesForStage } from '../constants/phases';
import { getStageColorClasses } from '../utils/phaseColors';

const STORAGE_KEY = 'classification-footnote-expanded';

export default function ClassificationFootnote({ onShowPhases }) {
  const [expanded, setExpanded] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) === 'true';
    } catch {
      return false;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, String(expanded));
    } catch {
      // ignore
    }
  }, [expanded]);

  return (
    <div className="mt-8 border border-gray-200 dark:border-slate-700 rounded-xl bg-gray-50 dark:bg-slate-800/60 overflow-hidden">
      {/* Header — sempre visível */}
      <button
        type="button"
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-center justify-between px-5 py-3 text-left
                   hover:bg-gray-100 dark:hover:bg-slate-700/60 transition-colors
                   focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-inset"
        aria-expanded={expanded}
      >
        <span className="flex items-center gap-2 text-sm font-semibold text-gray-600 dark:text-gray-400">
          <BookOpen className="h-4 w-4 text-indigo-500" aria-hidden="true" />
          Referência de Classificação Processual — Modelo Hierárquico PGM-Rio
        </span>
        {expanded
          ? <ChevronUp className="h-4 w-4 text-gray-400 shrink-0" aria-hidden="true" />
          : <ChevronDown className="h-4 w-4 text-gray-400 shrink-0" aria-hidden="true" />
        }
      </button>

      {/* Conteúdo expansível */}
      {expanded && (
        <div className="px-5 pb-5 pt-1 border-t border-gray-200 dark:border-slate-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-4 leading-relaxed">
            As classificações seguem as 5 fases processuais definidas pela Coordenação de Tecnologia da
            PGM-Rio, baseadas nas Tabelas Processuais Unificadas do CNJ (Res. 46/2007 e 326/2020) e no
            Modelo Nacional de Interoperabilidade (Res. CNJ 455/2022). A classificação usa 3 campos
            independentes: <strong>(1) Fase</strong>, <strong>(2) Subfases - para conhecimento e execução</strong> e se houve <strong>(3) Trânsito em Julgado da fase de conhecimento</strong>.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
            {Object.values(STAGES).map(stage => {
              const substages = getSubstagesForStage(stage.value);
              return (
                <div key={stage.value} className="space-y-1">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${getStageColorClasses(stage.value)}`}>
                    {stage.value}. {stage.label}
                  </span>
                  {substages.length > 0 && (
                    <ul className="ml-3 space-y-0.5 list-none p-0">
                      {substages.map(ss => (
                        <li key={ss.value} className="flex items-baseline gap-1.5 text-xs text-gray-600 dark:text-gray-400">
                          <span className="font-mono text-gray-400 shrink-0">{ss.value}</span>
                          <span>{ss.label}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              );
            })}
          </div>

          {/* Trânsito em Julgado */}
          <div className="flex flex-wrap items-center gap-3 pt-3 border-t border-gray-200 dark:border-slate-700">
            <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">
              Trânsito em Julgado:
            </span>
            {Object.values(TRANSIT_OPTIONS).map(t => (
              <span
                key={t.value}
                className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-200 dark:bg-slate-700 text-gray-700 dark:text-gray-300 font-mono"
              >
                {t.value} = {t.label}
              </span>
            ))}
            <button
              type="button"
              onClick={onShowPhases}
              className="ml-auto text-xs font-semibold text-indigo-600 dark:text-indigo-400
                         hover:text-indigo-800 dark:hover:text-indigo-300 underline underline-offset-2
                         focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded"
            >
              Ver referência completa →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
