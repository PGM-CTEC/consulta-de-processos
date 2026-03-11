import React, { useState } from 'react';
import { X } from 'lucide-react';
import { PHASE_BY_CODE, VALID_PHASES } from '../constants/phases';
import { toast } from 'react-hot-toast';

/**
 * Modal para editar a fase de um processo
 * @param {Object} props
 * @param {boolean} props.isOpen - Se o modal está aberto
 * @param {string} props.processNumber - Número do processo
 * @param {string} props.currentPhase - Fase atual (código "02", etc)
 * @param {function} props.onClose - Callback ao fechar
 * @param {function} props.onSave - Callback ao salvar (recebe {phase, reason})
 */
export default function PhaseEditModal({
  isOpen,
  processNumber,
  currentPhase,
  onClose,
  onSave,
}) {
  const [selectedPhase, setSelectedPhase] = useState(currentPhase);
  const [reason, setReason] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  if (!isOpen) return null;

  const phaseOptions = Object.entries(VALID_PHASES).map(([, phase]) => ({
    code: phase.code,
    name: phase.name,
  }));

  const handleSave = async () => {
    if (!reason.trim()) {
      toast.error('Por favor, explique o motivo da mudança');
      return;
    }

    setIsSaving(true);
    try {
      const response = await fetch(
        `/processes/${processNumber}/phase`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            corrected_phase: selectedPhase,
            reason: reason.trim(),
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Erro ao salvar: ${response.statusText}`);
      }

      const result = await response.json();
      toast.success('Fase corrigida com sucesso!');
      onSave({ phase: selectedPhase, reason, correction: result });
      onClose();
    } catch (error) {
      console.error('Erro ao corrigir fase:', error);
      toast.error(`Erro: ${error.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleClose = () => {
    setSelectedPhase(currentPhase);
    setReason('');
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Editar Fase</h2>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700"
            aria-label="Fechar"
          >
            <X size={20} />
          </button>
        </div>

        {/* Processo */}
        <div className="mb-4 p-3 bg-gray-50 rounded">
          <p className="text-sm text-gray-600">Processo:</p>
          <p className="font-mono text-sm font-semibold text-gray-900">
            {processNumber}
          </p>
        </div>

        {/* Seletor de Fase */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nova Fase:
          </label>
          <select
            value={selectedPhase}
            onChange={(e) => setSelectedPhase(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {phaseOptions.map((phase) => (
              <option key={phase.code} value={phase.code}>
                {phase.code} - {phase.name}
              </option>
            ))}
          </select>
        </div>

        {/* Campo de Motivo */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Motivo da mudança: <span className="text-red-600">*</span>
          </label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Ex: Processo foi remetido à 2ª instância após revisão de documentação"
            maxLength={500}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
              resize-none font-sans"
          />
          <p className="text-xs text-gray-500 mt-1">
            {reason.length}/500 caracteres
          </p>
        </div>

        {/* Aviso */}
        <div className="mb-6 p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
          ℹ️ Esta mudança será armazenada com o motivo para treinamento do modelo de
          classificação automática.
        </div>

        {/* Botões */}
        <div className="flex gap-3">
          <button
            onClick={handleClose}
            disabled={isSaving}
            className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-md
              hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed
              font-medium text-sm"
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving || !reason.trim()}
            className="flex-1 px-4 py-2 text-white bg-blue-600 rounded-md
              hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed
              font-medium text-sm"
          >
            {isSaving ? 'Salvando...' : 'Salvar Correção'}
          </button>
        </div>
      </div>
    </div>
  );
}
