/**
 * Utility for consistent phase color styling across the application.
 *
 * Centralizes the logic for determining Tailwind CSS classes based on process phase.
 * Based on the PGM-Rio classification model (Version 2.0 - February 2026)
 */

import { getPhaseInfo, normalizePhase, VALID_PHASES, STAGES } from '../constants/phases';

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

  // Color mapping with distinct colors for all 15 phases + dark mode variants
  const colorMap = {
    'sky': 'bg-sky-100 text-sky-800 dark:bg-sky-900/40 dark:text-sky-300 border border-sky-200 dark:border-sky-800',
    'blue': 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 border border-blue-200 dark:border-blue-800',
    'indigo': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800',
    'violet': 'bg-violet-100 text-violet-800 dark:bg-violet-900/40 dark:text-violet-300 border border-violet-200 dark:border-violet-800',
    'purple': 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300 border border-purple-200 dark:border-purple-800',
    'fuchsia': 'bg-fuchsia-100 text-fuchsia-800 dark:bg-fuchsia-900/40 dark:text-fuchsia-300 border border-fuchsia-200 dark:border-fuchsia-800',
    'pink': 'bg-pink-100 text-pink-800 dark:bg-pink-900/40 dark:text-pink-300 border border-pink-200 dark:border-pink-800',
    'rose': 'bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300 border border-rose-200 dark:border-rose-800',
    'red': 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300 border border-red-200 dark:border-red-800',
    'orange': 'bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300 border border-orange-200 dark:border-orange-800',
    'amber': 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 border border-amber-200 dark:border-amber-800',
    'yellow': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300 border border-yellow-200 dark:border-yellow-800',
    'lime': 'bg-lime-100 text-lime-800 dark:bg-lime-900/40 dark:text-lime-300 border border-lime-200 dark:border-lime-800',
    'green': 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300 border border-green-200 dark:border-green-800',
    'slate': 'bg-slate-100 text-slate-800 dark:bg-slate-900/40 dark:text-slate-300 border border-slate-200 dark:border-slate-800',
  };

  return colorMap[phaseInfo.color] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/40 dark:text-gray-300 border border-gray-200 dark:border-gray-800';
}

/**
 * Get Tailwind CSS background color class for a phase's progress bar
 *
 * @param {string} phase - The process phase name or code
 * @returns {string} Tailwind CSS background class
 */
export function getPhaseProgressBarClasses(phase) {
  const phaseInfo = getPhaseInfo(phase);

  const colorMap = {
    'sky': 'bg-sky-500 dark:bg-sky-400',
    'blue': 'bg-blue-500 dark:bg-blue-400',
    'indigo': 'bg-indigo-500 dark:bg-indigo-400',
    'violet': 'bg-violet-500 dark:bg-violet-400',
    'purple': 'bg-purple-500 dark:bg-purple-400',
    'fuchsia': 'bg-fuchsia-500 dark:bg-fuchsia-400',
    'pink': 'bg-pink-500 dark:bg-pink-400',
    'rose': 'bg-rose-500 dark:bg-rose-400',
    'red': 'bg-red-500 dark:bg-red-400',
    'orange': 'bg-orange-500 dark:bg-orange-400',
    'amber': 'bg-amber-500 dark:bg-amber-400',
    'yellow': 'bg-yellow-500 dark:bg-yellow-400',
    'lime': 'bg-lime-500 dark:bg-lime-400',
    'green': 'bg-green-500 dark:bg-green-400',
    'slate': 'bg-slate-500 dark:bg-slate-400',
  };

  return colorMap[phaseInfo.color] || 'bg-gray-500 dark:bg-gray-400';
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
 * Get Tailwind CSS classes for a stage (hierarchical classification)
 *
 * @param {number} stage - Stage number (1-5)
 * @returns {string} Tailwind CSS classes for styling the stage badge
 */
export function getStageColorClasses(stage) {
  const stageInfo = STAGES[stage];
  if (!stageInfo) return 'bg-gray-100 text-gray-800 dark:bg-gray-900/40 dark:text-gray-300 border border-gray-200 dark:border-gray-800';

  const colorMap = {
    'blue': 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 border border-blue-200 dark:border-blue-800',
    'orange': 'bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300 border border-orange-200 dark:border-orange-800',
    'lime': 'bg-lime-100 text-lime-800 dark:bg-lime-900/40 dark:text-lime-300 border border-lime-200 dark:border-lime-800',
    'slate': 'bg-slate-100 text-slate-800 dark:bg-slate-900/40 dark:text-slate-300 border border-slate-200 dark:border-slate-800',
    'green': 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300 border border-green-200 dark:border-green-800',
  };

  return colorMap[stageInfo.color] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/40 dark:text-gray-300 border border-gray-200 dark:border-gray-800';
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
