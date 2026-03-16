import { useState, useEffect, useRef } from 'react';
import { X } from 'lucide-react';
import { ALL_PHASES } from '../constants/phases';
import { submitPhaseCorrection } from '../services/phaseCorrections';

export default function PhaseEditModal({
  processNumber,
  currentPhase,
  classificationLog,
  sourceTab,
  onClose,
  onSuccess,
}) {
  const [selectedPhase, setSelectedPhase] = useState('');
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const closeRef = useRef(null);

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
  const isFormValid = selectedPhase && isReasonValid && !isSubmitting;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!isFormValid) return;

    setIsSubmitting(true);
    try {
      await submitPhaseCorrection(processNumber, {
        corrected_phase: selectedPhase,
        reason: reason.trim(),
        source_tab: sourceTab,
        original_phase: currentPhase,
        classification_log_snapshot: classificationLog,
      });

      // Sucesso: chamar onSuccess e fechar
      onSuccess?.(selectedPhase);
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
          {/* Fase Atual (Read-only) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Fase Atual
            </label>
            <div className="px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg
                            border border-gray-300 dark:border-gray-600
                            text-gray-900 dark:text-white">
              {currentPhase || 'Não informada'}
            </div>
          </div>

          {/* Seleção de Fase */}
          <div>
            <label htmlFor="phase-select" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Nova Fase <span className="text-red-500">*</span>
            </label>
            <select
              id="phase-select"
              value={selectedPhase}
              onChange={(e) => setSelectedPhase(e.target.value)}
              className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600
                         rounded-lg text-gray-900 dark:text-white
                         focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Selecione uma fase...</option>
              {ALL_PHASES.map((phase) => (
                <option key={phase.code} value={phase.code}>
                  {phase.code} - {phase.name}
                </option>
              ))}
            </select>
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
