/**
 * Utility for consistent phase color styling across the application.
 *
 * Centralizes the logic for determining Tailwind CSS classes based on process phase.
 */

/**
 * Get Tailwind CSS classes for a given process phase
 *
 * @param {string} phase - The process phase name
 * @returns {string} Tailwind CSS classes for styling the phase badge
 *
 * @example
 * getPhaseColorClasses('Execução')
 * // returns 'bg-orange-100 text-orange-800'
 */
export function getPhaseColorClasses(phase) {
  const phaseMap = {
    'Execução': 'bg-orange-100 text-orange-800',
    'Fase Executiva': 'bg-orange-100 text-orange-800',
    'Trânsito em Julgado': 'bg-green-100 text-green-800',
    'Arquivado / Baixa Definitiva': 'bg-gray-100 text-gray-800',
    'Arquivado': 'bg-gray-100 text-gray-800',
    'Conhecimento': 'bg-blue-100 text-blue-800',
  };

  return phaseMap[phase] || 'bg-blue-100 text-blue-800'; // Default to blue (Conhecimento)
}

/**
 * Get a human-readable phase name with fallback
 *
 * @param {string} phase - The process phase name
 * @returns {string} Formatted phase name or default
 */
export function getPhaseDisplayName(phase) {
  return phase || 'Conhecimento';
}

/**
 * Check if a phase is terminal (process is closed)
 *
 * @param {string} phase - The process phase name
 * @returns {boolean} True if the phase indicates the process is closed
 */
export function isTerminalPhase(phase) {
  const terminalPhases = [
    'Arquivado / Baixa Definitiva',
    'Arquivado',
    'Baixa Definitiva',
  ];

  return terminalPhases.includes(phase);
}

/**
 * Get phase icon emoji (optional, for future use)
 *
 * @param {string} phase - The process phase name
 * @returns {string} Emoji representing the phase
 */
export function getPhaseIcon(phase) {
  const iconMap = {
    'Execução': '⚖️',
    'Fase Executiva': '⚖️',
    'Trânsito em Julgado': '✅',
    'Arquivado / Baixa Definitiva': '📦',
    'Arquivado': '📦',
    'Conhecimento': '📋',
  };

  return iconMap[phase] || '📋';
}
