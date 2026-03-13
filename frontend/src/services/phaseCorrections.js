import api from './api';

/**
 * Submeter uma correção de fase processual
 * @param {string} processNumber - Número do processo
 * @param {Object} data - Dados da correção
 * @param {string} data.corrected_phase - Código da fase corrigida (01-15)
 * @param {string} data.reason - Motivo da correção
 * @param {string} [data.source_tab] - Aba de origem (single|bulk|history)
 * @param {string} [data.original_phase] - Fase original (opcional)
 * @param {Object} [data.classification_log_snapshot] - Snapshot do log de classificação
 * @returns {Promise<Object>} Resposta do servidor
 */
export const submitPhaseCorrection = async (processNumber, data) => {
  const response = await api.post(`/processes/${processNumber}/phase-correction`, data);
  return response.data;
};

/**
 * Listar correções de fase
 * @param {Object} [params] - Parâmetros de query
 * @param {string} [params.process_number] - Filtrar por número do processo
 * @param {number} [params.limit] - Limite de registros (máx 1000)
 * @param {number} [params.offset] - Offset para paginação
 * @returns {Promise<Array>} Lista de correções
 */
export const listPhaseCorrections = async (params = {}) => {
  const response = await api.get('/phase-corrections', { params });
  return response.data;
};
