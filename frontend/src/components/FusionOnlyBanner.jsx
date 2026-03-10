import { AlertCircle, X } from 'lucide-react';
import { useState } from 'react';

/**
 * FusionOnlyBanner — Exibe aviso prominente indicando que a classificação
 * de fases vem EXCLUSIVAMENTE do Fusion PAV/MNI.
 *
 * Componente específico para a branch: feature/fusion-only-classification
 */
export default function FusionOnlyBanner() {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <div
      className="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border-l-4 border-amber-500 dark:border-amber-600 shadow-md"
      role="alert"
      aria-live="polite"
      aria-label="Aviso: modo Fusion-only ativo"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-start gap-4">
        <AlertCircle
          className="h-5 w-5 text-amber-600 dark:text-amber-500 mt-0.5 flex-shrink-0"
          aria-hidden="true"
        />

        <div className="flex-grow">
          <h2 className="text-sm font-bold text-amber-900 dark:text-amber-100 mb-1">
            ⚠️ Modo Experimental: Classificação via Fusion PAV/MNI
          </h2>
          <p className="text-sm text-amber-800 dark:text-amber-200 leading-relaxed">
            <strong>Dados obtidos exclusivamente a partir da consulta ao Movimento Processual (MNI) do PAV/Fusion.</strong>
            As fases processuais nesta versão são calculadas utilizando apenas o DocumentPhaseClassifier com base nos
            &quot;batismos&quot; (movimentos) do Fusion. O DataJud fornece dados cadastrais complementares
            (tribunal, vara, classe, distribuição).
          </p>
          <p className="text-xs text-amber-700 dark:text-amber-300 mt-2 font-semibold">
            Branch: <code className="bg-amber-100 dark:bg-amber-900/50 px-2 py-0.5 rounded font-mono">feature/fusion-only-classification</code>
          </p>
        </div>

        <button
          onClick={() => setDismissed(true)}
          className="flex-shrink-0 p-1 text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 hover:bg-amber-100 dark:hover:bg-amber-900/30 rounded transition-colors focus:outline-none focus:ring-2 focus:ring-amber-500"
          aria-label="Fechar aviso"
          title="Fechar aviso"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
