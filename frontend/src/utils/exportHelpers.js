/**
 * Export utilities for bulk search results
 *
 * Provides reusable functions for exporting data in multiple formats:
 * - CSV (Comma-Separated Values)
 * - XLSX (Excel Spreadsheet)
 * - TXT (Plain Text)
 * - MD (Markdown Table)
 */

import * as XLSX from 'xlsx';
import { normalizePhaseWithMovements } from '../constants/phases';

/**
 * Transform process results into exportable format
 *
 * @param {Array} results - Array of process objects from API
 * @returns {Array} Array of objects with formatted data for export
 */
export function prepareExportData(results) {
  return results.map(p => ({
    'Número': p.number,
    'Tribunal': p.tribunal_name || p.court?.split(' - ')[0] || 'N/A',
    'Sede / Vara': p.court_unit || p.court?.split(' - ')[1] || p.court || 'N/A',
    'Fase Atual': normalizePhaseWithMovements(p.phase, p.class_nature, p.movements),
    'Fonte da Fase': p.phase_source || 'datajud'
  }));
}

/**
 * Export data to CSV format
 *
 * @param {Array} data - Prepared export data
 * @returns {string} CSV content as string
 */
export function generateCSV(data) {
  const headers = ['Número', 'Tribunal', 'Sede / Vara', 'Fase Atual', 'Fonte da Fase'];
  const csvContent = [
    headers.join(','),
    ...data.map(row => Object.values(row).map(v => `"${v}"`).join(','))
  ].join('\n');

  return csvContent;
}

/**
 * Export data to XLSX format and trigger download
 *
 * @param {Array} data - Prepared export data
 * @param {string} filename - Optional filename (without extension)
 */
export function exportToXLSX(data, filename = `consulta_lote_${Date.now()}`) {
  const worksheet = XLSX.utils.json_to_sheet(data);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Processos');
  XLSX.writeFile(workbook, `${filename}.xlsx`);
}

/**
 * Export data to TXT format (pipe-separated)
 *
 * @param {Array} data - Prepared export data
 * @returns {string} TXT content as string
 */
export function generateTXT(data) {
  return data.map(row =>
    `${row['Número']} | ${row['Tribunal']} | ${row['Sede / Vara']} | ${row['Fase Atual']}`
  ).join('\n');
}

/**
 * Export data to Markdown table format
 *
 * @param {Array} data - Prepared export data
 * @returns {string} Markdown table as string
 */
export function generateMarkdown(data) {
  const headers = ['Número', 'Tribunal', 'Sede / Vara', 'Fase Atual'];
  const mdHeader = `| ${headers.join(' | ')} |`;
  const mdDivider = `| ${headers.map(() => '---').join(' | ')} |`;
  const mdRows = data.map(row => `| ${Object.values(row).join(' | ')} |`).join('\n');

  return `${mdHeader}\n${mdDivider}\n${mdRows}`;
}

/**
 * Generic download function for text-based files
 *
 * @param {string} content - File content
 * @param {string} extension - File extension (without dot)
 * @param {string} mimeType - MIME type for the file
 * @param {string} filename - Optional filename (without extension)
 */
export function downloadFile(content, extension, mimeType, filename = `consulta_lote_${Date.now()}`) {
  const blob = new Blob([content], { type: `${mimeType};charset=utf-8;` });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');

  link.href = url;
  link.setAttribute('download', `${filename}.${extension}`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  // Clean up the URL object
  URL.revokeObjectURL(url);
}

/**
 * High-level export functions for different formats
 */
export const exporters = {
  /**
   * Export to CSV format
   * @param {Array} results - Process results from API
   * @param {string} filename - Optional filename
   */
  csv: (results, filename) => {
    const data = prepareExportData(results);
    const content = generateCSV(data);
    downloadFile(content, 'csv', 'text/csv', filename);
  },

  /**
   * Export to XLSX format
   * @param {Array} results - Process results from API
   * @param {string} filename - Optional filename
   */
  xlsx: (results, filename) => {
    const data = prepareExportData(results);
    exportToXLSX(data, filename);
  },

  /**
   * Export to TXT format
   * @param {Array} results - Process results from API
   * @param {string} filename - Optional filename
   */
  txt: (results, filename) => {
    const data = prepareExportData(results);
    const content = generateTXT(data);
    downloadFile(content, 'txt', 'text/plain', filename);
  },

  /**
   * Export to Markdown format
   * @param {Array} results - Process results from API
   * @param {string} filename - Optional filename
   */
  md: (results, filename) => {
    const data = prepareExportData(results);
    const content = generateMarkdown(data);
    downloadFile(content, 'md', 'text/markdown', filename);
  },
};
