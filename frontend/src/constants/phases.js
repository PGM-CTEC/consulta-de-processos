/**
 * Constantes de Fases Processuais
 * Baseado no modelo de classificação da PGM-Rio (Versão 2.0 - Fevereiro 2026)
 *
 * Este arquivo define as 15 fases processuais oficiais e suas propriedades.
 */

/**
 * Definição das 15 fases processuais oficiais
 */
export const VALID_PHASES = {
  // Fases de Conhecimento (01-09)
  CONHECIMENTO_ANTES_SENTENCA: {
    code: '01',
    name: 'Conhecimento — Antes da Sentença',
    type: 'Conhecimento',
    color: 'sky'
  },
  CONHECIMENTO_SENTENCA_SEM_TRANSITO: {
    code: '02',
    name: 'Conhecimento — Sentença sem Trânsito em Julgado',
    type: 'Conhecimento',
    color: 'blue'
  },
  CONHECIMENTO_SENTENCA_COM_TRANSITO: {
    code: '03',
    name: 'Conhecimento — Sentença com Trânsito em Julgado',
    type: 'Conhecimento',
    color: 'indigo'
  },
  CONHECIMENTO_RECURSO_2_PENDENTE: {
    code: '04',
    name: 'Conhecimento — Recurso 2ª Instância — Pendente Julgamento',
    type: 'Conhecimento',
    color: 'violet'
  },
  CONHECIMENTO_RECURSO_2_JULGADO: {
    code: '05',
    name: 'Conhecimento — Recurso 2ª Instância — Julgado sem Trânsito',
    type: 'Conhecimento',
    color: 'purple'
  },
  CONHECIMENTO_RECURSO_2_TRANSITADO: {
    code: '06',
    name: 'Conhecimento — Recurso 2ª Instância — Transitado em Julgado',
    type: 'Conhecimento',
    color: 'fuchsia'
  },
  CONHECIMENTO_RECURSO_SUP_PENDENTE: {
    code: '07',
    name: 'Conhecimento — Recurso Tribunais Superiores — Pendente Julgamento',
    type: 'Conhecimento',
    color: 'pink'
  },
  CONHECIMENTO_RECURSO_SUP_JULGADO: {
    code: '08',
    name: 'Conhecimento — Recurso Tribunais Superiores — Julgado sem Trânsito',
    type: 'Conhecimento',
    color: 'rose'
  },
  CONHECIMENTO_RECURSO_SUP_TRANSITADO: {
    code: '09',
    name: 'Conhecimento — Recurso Tribunais Superiores — Transitado em Julgado',
    type: 'Conhecimento',
    color: 'red'
  },

  // Fases de Execução (10-12, 14)
  EXECUCAO: {
    code: '10',
    name: 'Execução',
    type: 'Execução',
    color: 'orange'
  },
  EXECUCAO_SUSPENSA: {
    code: '11',
    name: 'Execução Suspensa',
    type: 'Execução',
    color: 'amber'
  },
  EXECUCAO_SUSPENSA_PARCIAL: {
    code: '12',
    name: 'Execução Suspensa Parcialmente',
    type: 'Execução',
    color: 'yellow'
  },
  CONVERSAO_RENDA: {
    code: '14',
    name: 'Conversão em Renda',
    type: 'Execução',
    color: 'green'
  },

  // Fases Transversais e Finais (13, 15)
  SUSPENSO_SOBRESTADO: {
    code: '13',
    name: 'Suspenso / Sobrestado',
    type: 'Transversal',
    color: 'lime'
  },
  ARQUIVADO: {
    code: '15',
    name: 'Arquivado Definitivamente',
    type: 'Final',
    color: 'slate'
  }
};

/**
 * Array com todas as fases para facilitar iteração
 */
export const ALL_PHASES = Object.values(VALID_PHASES);

/**
 * Mapeamento de código para fase
 */
export const PHASE_BY_CODE = ALL_PHASES.reduce((acc, phase) => {
  acc[phase.code] = phase;
  return acc;
}, {});

/**
 * Mapeamento de nome para fase
 */
export const PHASE_BY_NAME = ALL_PHASES.reduce((acc, phase) => {
  acc[phase.name] = phase;
  return acc;
}, {});

/**
 * Classes processuais que indicam execução
 */
const EXECUTION_CLASSES = [
  'execução',
  'cumprimento de sentença',
  'cumprimento de sentenca',
  'execução fiscal',
  'execucao fiscal',
  'execução de título',
  'execucao de titulo',
  'cumprimento',
];

/**
 * Verifica se uma classe processual é de execução
 * @param {string} classNature - Classe processual
 * @returns {boolean}
 */
function isExecutionClass(classNature) {
  if (!classNature) return false;
  const lower = classNature.toLowerCase();
  return EXECUTION_CLASSES.some(exec => lower.includes(exec));
}

/**
 * Normaliza uma string de fase para o nome oficial.
 *
 * ATENÇÃO: Esta função normaliza STRINGS de fase — ela NÃO consulta movimentos
 * do processo. Para classificação que considera o contexto completo de movimentos
 * (ex: detectar baixa definitiva revertida por desarquivamento), use
 * normalizePhaseWithMovements().
 *
 * @param {string} phaseInput - Fase recebida do backend
 * @param {string} classNature - Classe processual (opcional, melhora a precisão)
 * @returns {string} Nome oficial da fase ou fase padrão
 */
export function normalizePhase(phaseInput, classNature = null) {
  if (!phaseInput) return VALID_PHASES.CONHECIMENTO_ANTES_SENTENCA.name;

  const input = String(phaseInput).trim();
  const isExecution = classNature ? isExecutionClass(classNature) : false;

  // Verifica se é um código puro (01-15)
  if (/^0?\d{1,2}$/.test(input)) {
    const code = input.padStart(2, '0');
    return PHASE_BY_CODE[code]?.name || VALID_PHASES.CONHECIMENTO_ANTES_SENTENCA.name;
  }

  // Extrai código do início da string (ex: "02 Conhecimento - Sentença sem Trânsito em Julgado")
  // Evita que palavras-chave como "trânsito" sobrescrevam o código numérico explícito
  const codeAtStart = input.match(/^(\d{2})\s+/);
  if (codeAtStart) {
    const code = codeAtStart[1];
    const phaseByCode = PHASE_BY_CODE[code];
    if (phaseByCode) return phaseByCode.name;
  }

  // Normaliza traços/travessões para fazer comparação
  const normalizedInput = input.replace(/\s*[-–—]\s*/g, ' — ');

  // Verifica se já é um nome válido (após normalização)
  if (PHASE_BY_NAME[normalizedInput]) {
    return normalizedInput;
  }

  // Tenta fazer match por palavras-chave
  const inputLower = input.toLowerCase();

  // Fase 15 - Arquivado
  if (inputLower.includes('arquivado') || inputLower.includes('baixa definitiva')) {
    return VALID_PHASES.ARQUIVADO.name;
  }

  // Fase 13 - Suspenso/Sobrestado
  if (inputLower.includes('suspenso') || inputLower.includes('sobrestado')) {
    return VALID_PHASES.SUSPENSO_SOBRESTADO.name;
  }

  // Fase 14 - Conversão em Renda
  if (inputLower.includes('conversão') && inputLower.includes('renda')) {
    return VALID_PHASES.CONVERSAO_RENDA.name;
  }

  // Fases de Execução (10-12)
  // Se a classe é de execução OU a fase menciona execução
  if (isExecution || inputLower.includes('execução') || inputLower.includes('cumprimento')) {
    if (inputLower.includes('suspensa') && inputLower.includes('parcial')) {
      return VALID_PHASES.EXECUCAO_SUSPENSA_PARCIAL.name;
    }
    if (inputLower.includes('suspensa')) {
      return VALID_PHASES.EXECUCAO_SUSPENSA.name;
    }
    // Se a classe é execução e a fase menciona trânsito, ainda é execução (fase 10)
    // porque o trânsito aconteceu no processo de conhecimento anterior
    return VALID_PHASES.EXECUCAO.name;
  }

  // Helper: "transitado" ou "trânsito" sem "sem trânsito"/"sem transito" antes
  const hasTransito = (inputLower.includes('transitado') || inputLower.includes('trânsito')) &&
    !inputLower.includes('sem trânsito') && !inputLower.includes('sem transito');

  // Fases de Conhecimento (01-09)
  // Apenas processar como conhecimento se NÃO for classe de execução
  if (!isExecution) {
    if (inputLower.includes('conhecimento') || inputLower.includes('sentença') ||
      inputLower.includes('recurso') || inputLower.includes('transitado') ||
      inputLower.includes('trânsito') || inputLower.includes('julgado')) {

      // Tribunais Superiores (07-09)
      if (inputLower.includes('superior') || inputLower.includes('stj') || inputLower.includes('stf')) {
        if (hasTransito) {
          return VALID_PHASES.CONHECIMENTO_RECURSO_SUP_TRANSITADO.name;
        }
        if (inputLower.includes('julgado')) {
          return VALID_PHASES.CONHECIMENTO_RECURSO_SUP_JULGADO.name;
        }
        return VALID_PHASES.CONHECIMENTO_RECURSO_SUP_PENDENTE.name;
      }

      // 2ª Instância (04-06)
      if (inputLower.includes('2ª') || inputLower.includes('segunda') ||
        inputLower.includes('recurso') || inputLower.includes('2.')) {
        if (hasTransito) {
          return VALID_PHASES.CONHECIMENTO_RECURSO_2_TRANSITADO.name;
        }
        if (inputLower.includes('julgado')) {
          return VALID_PHASES.CONHECIMENTO_RECURSO_2_JULGADO.name;
        }
        return VALID_PHASES.CONHECIMENTO_RECURSO_2_PENDENTE.name;
      }

      // 1ª Instância (01-03)
      if (inputLower.includes('sentença')) {
        if (hasTransito) {
          return VALID_PHASES.CONHECIMENTO_SENTENCA_COM_TRANSITO.name;
        }
        return VALID_PHASES.CONHECIMENTO_SENTENCA_SEM_TRANSITO.name;
      }

      // Se só menciona trânsito em julgado (sem mais contexto), assume G1 com trânsito
      if (hasTransito) {
        return VALID_PHASES.CONHECIMENTO_SENTENCA_COM_TRANSITO.name;
      }
    }
  }

  // Fase padrão: se é execução -> Execução (10), senão -> Conhecimento (01)
  return isExecution ? VALID_PHASES.EXECUCAO.name : VALID_PHASES.CONHECIMENTO_ANTES_SENTENCA.name;
}

/**
 * Códigos de movimento CNJ que indicam baixa definitiva/arquivamento
 */
// Sincronizado com backend/services/phase_analyzer.py: CODIGOS_BAIXA
// NOTA: 246 = "Proferida Sentença" (CNJ) — NÃO é código de baixa
const MOVIMENTO_BAIXA_CODES = [22, 861, 865, 10965, 10966, 10967, 12618];

/**
 * Verifica se há movimento de baixa definitiva nos dados do processo
 * @param {Array} movements - Array de movimentos do processo
 * @returns {boolean} True se há movimento de baixa não revertido
 */
export function hasDefinitiveBaixa(movements) {
  if (!movements || !Array.isArray(movements)) return false;

  // Procurar movimento de baixa
  const baixaMovement = movements.find(m =>
    MOVIMENTO_BAIXA_CODES.includes(parseInt(m.code)) ||
    MOVIMENTO_BAIXA_CODES.includes(parseInt(m.codigo))
  );

  if (!baixaMovement) return false;

  // Verificar se há desarquivamento posterior
  // Sincronizado com backend/services/phase_analyzer.py: CODIGOS_REATIVACAO
  const baixaDate = new Date(baixaMovement.date || baixaMovement.dataHora);
  const CODIGOS_DESARQUIVAMENTO = [900, 12617, 849, 36];

  const hasDesarquivamento = movements.some(m => {
    const code = parseInt(m.code || m.codigo);
    if (!CODIGOS_DESARQUIVAMENTO.includes(code)) return false;

    const movDate = new Date(m.date || m.dataHora);
    return movDate > baixaDate;
  });

  return !hasDesarquivamento;
}

/**
 * Normaliza fase considerando também os movimentos do processo
 * Útil para corrigir classificações incorretas do backend
 * @param {string} phaseInput - Fase recebida do backend
 * @param {string} classNature - Classe processual
 * @param {Array} movements - Movimentos do processo
 * @returns {string} Nome oficial da fase
 */
export function normalizePhaseWithMovements(phaseInput, classNature = null, movements = null) {
  // Respeita phase_override do backend (ex: "Indefinido" quando 1ª instância ausente)
  if (phaseInput === 'Indefinido') {
    return 'Indefinido';
  }

  // Se há movimento de baixa definitiva, força Fase 15
  if (movements && hasDefinitiveBaixa(movements)) {
    return VALID_PHASES.ARQUIVADO.name;
  }

  // Caso contrário, usa normalização padrão
  return normalizePhase(phaseInput, classNature);
}

/**
 * Verifica se uma fase é válida
 * @param {string} phase - Nome da fase
 * @returns {boolean}
 */
export function isValidPhase(phase) {
  return !!PHASE_BY_NAME[phase];
}

/**
 * Obtém informações completas de uma fase
 * @param {string} phaseInput - Nome ou código da fase
 * @param {string} classNature - Classe processual (opcional)
 * @returns {object} Objeto com informações da fase
 */
export function getPhaseInfo(phaseInput, classNature = null) {
  const normalizedName = normalizePhase(phaseInput, classNature);
  return PHASE_BY_NAME[normalizedName] || VALID_PHASES.CONHECIMENTO_ANTES_SENTENCA;
}


// ============================================================
// Classificação Hierárquica — 3 Campos Independentes
// ============================================================

/**
 * Stages (Campo 1): Estágio principal do processo
 */
export const STAGES = {
  1: { value: 1, label: 'Conhecimento', color: 'blue' },
  2: { value: 2, label: 'Execução', color: 'orange' },
  3: { value: 3, label: 'Suspensão / Sobrestamento', color: 'lime' },
  4: { value: 4, label: 'Arquivamento', color: 'slate' },
  5: { value: 5, label: 'Conversão em Renda', color: 'green' },
};

/**
 * Substages (Campo 2): Subfase dentro do stage
 */
export const SUBSTAGES = {
  '1.1': { value: '1.1', label: 'Antes da Sentença', stage: 1 },
  '1.2': { value: '1.2', label: 'Sentença Proferida', stage: 1 },
  '1.3': { value: '1.3', label: 'Pendente Julgamento Tribunal Local', stage: 1 },
  '1.4': { value: '1.4', label: 'Julgamento no Tribunal (Monocrático ou Acórdão)', stage: 1 },
  '1.5': { value: '1.5', label: 'Pendente Julgamento Tribunal Superior', stage: 1 },
  '1.6': { value: '1.6', label: 'Julgamento no Tribunal Superior (Monocrático ou Acórdão)', stage: 1 },
  '2.1': { value: '2.1', label: 'Execução Normal', stage: 2 },
  '2.2': { value: '2.2', label: 'Execução Suspensa Parcialmente', stage: 2 },
  '2.3': { value: '2.3', label: 'Execução Suspensa', stage: 2 },
};

/**
 * Transit (Campo 3): Trânsito em julgado
 */
export const TRANSIT_OPTIONS = {
  sim: { value: 'sim', label: 'Sim' },
  nao: { value: 'nao', label: 'Não' },
  na:  { value: 'na',  label: 'N/A' },
};

/**
 * Retorna substages filtradas por stage
 * @param {number} stage
 * @returns {Array<{value: string, label: string}>}
 */
export function getSubstagesForStage(stage) {
  return Object.values(SUBSTAGES).filter(s => s.stage === stage);
}

/**
 * Formata a classificação hierárquica para exibição
 * @param {object} classification - {stage, stage_label, substage, substage_label, transit_julgado}
 * @returns {string}
 */
export function formatClassification(classification) {
  if (!classification || !classification.stage) return null;

  const stageLabel = classification.stage_label || STAGES[classification.stage]?.label || '';
  const substageLabel = classification.substage_label || SUBSTAGES[classification.substage]?.label || '';
  const transit = classification.transit_julgado;

  let parts = [stageLabel];
  if (substageLabel) parts.push(substageLabel);
  if (transit === 'sim') parts.push('(Trânsito em Julgado)');

  return parts.join(' — ');
}
