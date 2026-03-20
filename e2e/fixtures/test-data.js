/**
 * E2E Test Data and Fixtures
 * Shared test data for E2E tests
 */

export const VALID_PROCESS_NUMBERS = [
  '00000001010000100001', // Valid CNJ process number format
  '00000001010000100002',
];

export const INVALID_PROCESS_NUMBERS = [
  'invalid-number',
  '123', // Too short
  '',    // Empty
];

export const BULK_PROCESS_NUMBERS = [
  '00000001010000100001',
  '00000001010000100002',
  '00000001010000100003',
];

export const API_TIMEOUTS = {
  SHORT: 5000,
  MEDIUM: 10000,
  LONG: 30000,
};

export const SELECTORS = {
  // SearchProcess component
  SEARCH_INPUT: 'input[type="text"]',
  SEARCH_BUTTON: 'button:has-text("Buscar")',
  LOADING_SPINNER: '[role="status"]',
  ERROR_MESSAGE: '[role="alert"]',

  // ProcessDetails component
  PROCESS_NUMBER: 'text=/\\d{20}/',
  TRIBUNAL_NAME: 'text=/TJ[A-Z]{2}/',
  CLASS_NATURE: '[data-testid="class-nature"]',
  PHASE_INFO: '[data-testid="phase"]',
  MOVEMENTS_LIST: '[data-testid="movements"]',

  // BulkSearch component
  BULK_TEXTAREA: 'textarea',
  BULK_SEARCH_BUTTON: 'button:has-text("Processar Lote")',
  BULK_RESULTS: '[data-testid="bulk-results"]',
  BULK_FAILURES: '[data-testid="bulk-failures"]',

  // Export buttons
  EXPORT_CSV: 'button:has-text("CSV")',
  EXPORT_EXCEL: 'button:has-text("Excel")',
  EXPORT_JSON: 'button:has-text("JSON")',

  // Navigation
  SEARCH_TAB: 'button:has-text("Busca Individual")',
  BULK_TAB: 'button:has-text("Busca em Lote")',
  ANALYTICS_TAB: 'button:has-text("Análise")',
};

export const WAIT_TIMES = {
  ELEMENT_VISIBLE: 5000,
  NAVIGATION: 3000,
  API_RESPONSE: 10000,
  FILE_DOWNLOAD: 5000,
};
