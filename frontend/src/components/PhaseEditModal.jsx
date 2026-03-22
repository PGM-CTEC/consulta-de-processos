import { useState, useEffect, useRef } from 'react';
import { X } from 'lucide-react';
import { STAGES, SUBSTAGES, TRANSIT_OPTIONS, getSubstagesForStage, hierarchyToLegacyPhase } from '../constants/phases';
import { submitPhaseCorrection } from '../services/phaseCorrections';

export default function PhaseEditModal({
  processNumber,
  currentPhase,
  currentClassification,
  classificationLog,
  sourceTab,
  onClose,
  onSuccess,
}) {
  const [selectedStage, setSelectedStage] = useState('');
  const [selectedSubstage, setSelectedSubstage] = useState('');
  const [selectedTransit, setSelectedTransit] = useState('');
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const closeRef = useRef(null);

  const availableSubstages = selectedStage ? getSubstagesForStage(Number(selectedStage)) : [];

  // Setup Escape key handler e focus
  useEffect(() => {
    const handle = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handle);
    closeRef.current?.focus();
    return () => document.removeEventListener('keydown', handle);
  }, [onClose]);

  // Validações
  const isReasonValid = reason.trim().length >= 10;
  const isFormValid = selectedStage && isReasonValid && !isSubmitting;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!isFormValid) return;

    const correctedPhase = hierarchyToLegacyPhase(selectedStage, selectedSubstage, selectedTransit);

    setIsSubmitting(true);
    try {
      await submitPhaseCorrection(processNumber, {
        corrected_phase: correctedPhase,
        corrected_stage: Number(selectedStage),
        corrected_substage: selectedSubstage || undefined,
        corrected_transit: selectedTransit || undefined,
        reason: reason.trim(),
        source_tab: sourceTab,
        original_phase: currentPhase,
        classification_log_snapshot: classificationLog,
      });

      // Sucesso: chamar onSuccess e fechar
      onSuccess?.(correctedPhase);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao salvar correção. Tente novamente.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      aria-hidden="false"
    >
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Dialog */}
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="phase-edit-title"
        className="relative z-10 bg-white dark:bg-gray-900 rounded-2xl shadow-2xl
                   w-full max-w-md mx-4"
      >
        {/* Header */}
        <div className="flex items-center justify-between
                        bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700
                        px-6 py-4 rounded-t-2xl">
          <h2 id="phase-edit-title"
              className="text-lg font-bold text-gray-900 dark:text-white">
            Corrigir Fase Processual
          </h2>
          <button
            ref={closeRef}
            onClick={onClose}
            aria-label="Fechar"
            className="p-1 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200
                       hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors
                       focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Conteúdo */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Classificação Atual (Read-only) */}
          {currentClassification?.stage && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Classificação Atual
              </label>
              <div className="px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg border border-gray-300 dark:border-gray-600 flex items-center gap-2 flex-wrap text-sm">
                <span className="font-medium text-gray-900 dark:text-white">
                  {currentClassification.stage_label || STAGES[currentClassification.stage]?.label}
                </span>
                {currentClassification.substage && (
                  <span className="text-gray-500 dark:text-gray-400">
                    / {currentClassification.substage_label || SUBSTAGES[currentClassification.substage]?.label}
                  </span>
                )}
                {currentClassification.transit_julgado && (
                  <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${
                    currentClassification.transit_julgado === 'sim'
                      ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                      : currentClassification.transit_julgado === 'nao'
                      ? 'bg-gray-100 text-gray-600 border border-gray-200'
                      : 'bg-slate-100 text-slate-500 border border-slate-200'
                  }`}>
                    Trâns. Julg.: {TRANSIT_OPTIONS[currentClassification.transit_julgado]?.label || currentClassification.transit_julgado}
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Classificação Hierárquica (3 campos obrigatório) */}
          <div className="space-y-3 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              Nova Classificação <span className="text-red-500">*</span>
            </p>
            <div className="grid grid-cols-3 gap-2">
              <div>
                <label htmlFor="stage-select" className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                  Estágio <span className="text-red-500">*</span>
                </label>
                <select
                  id="stage-select"
                  value={selectedStage}
                  onChange={(e) => {
                    setSelectedStage(e.target.value);
                    setSelectedSubstage('');
                  }}
                  className="w-full px-2 py-1.5 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600
                             rounded-lg text-gray-900 dark:text-white
                             focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">—</option>
                  {Object.values(STAGES).map((s) => (
                    <option key={s.value} value={s.value}>
                      {s.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="substage-select" className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                  Subfase
                </label>
                <select
                  id="substage-select"
                  value={selectedSubstage}
                  onChange={(e) => setSelectedSubstage(e.target.value)}
                  disabled={!selectedStage || availableSubstages.length === 0}
                  className="w-full px-2 py-1.5 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600
                             rounded-lg text-gray-900 dark:text-white disabled:opacity-50
                             focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">—</option>
                  {availableSubstages.map((ss) => (
                    <option key={ss.value} value={ss.value}>
                      {ss.value} — {ss.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="transit-select" className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                  Trânsito
                </label>
                <select
                  id="transit-select"
                  value={selectedTransit}
                  onChange={(e) => setSelectedTransit(e.target.value)}
                  className="w-full px-2 py-1.5 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600
                             rounded-lg text-gray-900 dark:text-white
                             focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">—</option>
                  {Object.values(TRANSIT_OPTIONS).map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Motivo da Correção */}
          <div>
            <label htmlFor="reason" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Motivo <span className="text-red-500">*</span>
            </label>
            <textarea
              id="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Descreva o motivo da correção (mínimo 10 caracteres)"
              rows="4"
              className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600
                         rounded-lg text-gray-900 dark:text-white placeholder-gray-400
                         focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <div className="text-right text-xs text-gray-500 dark:text-gray-400 mt-1">
              {reason.length}/2000
            </div>
          </div>

          {/* Mensagem de Erro */}
          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800
                            rounded-lg text-sm text-red-700 dark:text-red-300">
              {error}
            </div>
          )}

          {/* Botões */}
          <div className="flex gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white
                         rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600
                         transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={!isFormValid}
              className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium
                         hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed
                         transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {isSubmitting ? 'Salvando...' : 'Salvar Correção'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
