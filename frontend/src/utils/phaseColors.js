/**
 * Utility for consistent phase color styling across the application.
 *
 * Centralizes the logic for determining Tailwind CSS classes based on process phase.
 * Based on the PGM-Rio classification model (Version 2.0 - February 2026)
 */

import { getPhaseInfo, normalizePhase, VALID_PHASES } from '../constants/phases';

/**
 * Get Tailwind CSS classes for a given process phase
 *
 * @param {string} phase - The process phase name or code
 * @param {string} classNature - Optional class nature to improve classification accuracy
 * @returns {string} Tailwind CSS classes for styling the phase badge
 *
 * @example
 * getPhaseColorClasses('Execução')
 * // returns 'bg-orange-100 text-orange-800'
 */
export function getPhaseColorClasses(phase, classNature = null) {
  const phaseInfo = getPhaseInfo(phase, classNature);

  // Color mapping based on phase color property
  const colorMap = {
    'blue': 'bg-blue-100 text-blue-800',
    'green': 'bg-green-100 text-green-800',
    'orange': 'bg-orange-100 text-orange-800',
    'yellow': 'bg-yellow-100 text-yellow-800',
    'purple': 'bg-purple-100 text-purple-800',
    'gray': 'bg-gray-100 text-gray-800'
  };

  return colorMap[phaseInfo.color] || 'bg-blue-100 text-blue-800';
}

/**
 * Get a normalized phase name for display
 *
 * @param {string} phase - The process phase name or code from backend
 * @param {string} classNature - Optional class nature to improve classification accuracy
 * @returns {string} Normalized phase name (one of the 15 valid phases)
 */
export function getPhaseDisplayName(phase, classNature = null) {
  return normalizePhase(phase, classNature);
}

/**
 * Check if a phase is terminal (process is closed)
 *
 * @param {string} phase - The process phase name
 * @returns {boolean} True if the phase indicates the process is closed
 */
export function isTerminalPhase(phase) {
  const normalizedPhase = normalizePhase(phase);
  return normalizedPhase === VALID_PHASES.ARQUIVADO.name;
}

/**
 * Get phase icon emoji (optional, for future use)
 *
 * @param {string} phase - The process phase name
 * @returns {string} Emoji representing the phase
 */
export function getPhaseIcon(phase) {
  const phaseInfo = getPhaseInfo(phase);

  const iconMap = {
    'Conhecimento': '📋',
    'Execução': '⚖️',
    'Transversal': '⏸️',
    'Final': '📦'
  };

  return iconMap[phaseInfo.type] || '📋';
}
