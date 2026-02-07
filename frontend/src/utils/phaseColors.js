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
// Matches roughly based on keywords or exact strings from classification_rules.py
export function getPhaseColorClasses(phase) {
  // Matches roughly based on keywords or exact strings from classification_rules.py
  const phaseLower = (phase || '').toLowerCase();

  if (phaseLower.includes('arquivado') || phaseLower.includes('baixa') || phaseLower.startsWith('15')) {
    return 'bg-gray-100 text-gray-800';
  }
  if (phaseLower.includes('execução') || phaseLower.startsWith('10') || phaseLower.startsWith('11') || phaseLower.startsWith('12')) {
    return 'bg-orange-100 text-orange-800';
  }
  if (phaseLower.includes('suspenso') || phaseLower.includes('sobrestado') || phaseLower.startsWith('13')) {
    return 'bg-yellow-100 text-yellow-800';
  }
  if (phaseLower.includes('transitad') || phaseLower.includes('trânsito') || phaseLower.includes('03') || phaseLower.includes('06') || phaseLower.includes('09')) {
    return 'bg-green-100 text-green-800';
  }
  if (phaseLower.includes('conversão') || phaseLower.startsWith('14')) {
    return 'bg-purple-100 text-purple-800';
  }

  // Default for Conhecimento (01, 02, 04, 05, 07, 08 and others)
  return 'bg-blue-100 text-blue-800';
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
