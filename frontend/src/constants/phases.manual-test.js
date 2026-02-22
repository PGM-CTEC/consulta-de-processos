/**
 * Testes básicos para o sistema de fases processuais
 * Execute com: npm test phases.test.js
 */

import { normalizePhase, getPhaseInfo, isValidPhase, VALID_PHASES } from './phases';

// Casos de teste
const testCases = [
  // Códigos numéricos
  { input: '01', expected: VALID_PHASES.CONHECIMENTO_ANTES_SENTENCA.name },
  { input: '1', expected: VALID_PHASES.CONHECIMENTO_ANTES_SENTENCA.name },
  { input: '10', expected: VALID_PHASES.EXECUCAO.name },
  { input: '15', expected: VALID_PHASES.ARQUIVADO.name },

  // Nomes completos (com travessão)
  { input: 'Conhecimento — Antes da Sentença', expected: VALID_PHASES.CONHECIMENTO_ANTES_SENTENCA.name },
  { input: 'Execução', expected: VALID_PHASES.EXECUCAO.name },
  { input: 'Arquivado Definitivamente', expected: VALID_PHASES.ARQUIVADO.name },

  // Nomes do backend (com traço)
  { input: 'Conhecimento - Antes da Sentença', expected: VALID_PHASES.CONHECIMENTO_ANTES_SENTENCA.name },
  { input: 'Conhecimento - Sentença sem Trânsito em Julgado', expected: VALID_PHASES.CONHECIMENTO_SENTENCA_SEM_TRANSITO.name },
  { input: 'Execução Suspensa', expected: VALID_PHASES.EXECUCAO_SUSPENSA.name },

  // Variações e palavras-chave
  { input: 'execução', expected: VALID_PHASES.EXECUCAO.name },
  { input: 'exec suspensa', expected: VALID_PHASES.EXECUCAO_SUSPENSA.name },
  { input: 'arquivado', expected: VALID_PHASES.ARQUIVADO.name },
  { input: 'suspenso', expected: VALID_PHASES.SUSPENSO_SOBRESTADO.name },
  { input: 'sobrestado', expected: VALID_PHASES.SUSPENSO_SOBRESTADO.name },
  { input: 'conversão em renda', expected: VALID_PHASES.CONVERSAO_RENDA.name },
  { input: 'conhecimento', expected: VALID_PHASES.CONHECIMENTO_ANTES_SENTENCA.name },

  // Casos edge
  { input: null, expected: VALID_PHASES.CONHECIMENTO_ANTES_SENTENCA.name },
  { input: '', expected: VALID_PHASES.CONHECIMENTO_ANTES_SENTENCA.name },
  { input: 'fase inválida', expected: VALID_PHASES.CONHECIMENTO_ANTES_SENTENCA.name },
];

function runTests() {
  console.log('🧪 Executando testes do sistema de fases processuais...\n');

  let passed = 0;
  let failed = 0;

  testCases.forEach(({ input, expected }, index) => {
    const result = normalizePhase(input);
    const isPass = result === expected;

    if (isPass) {
      passed++;
      console.log(`✅ Teste ${index + 1}: PASSOU`);
    } else {
      failed++;
      console.log(`❌ Teste ${index + 1}: FALHOU`);
      console.log(`   Input: "${input}"`);
      console.log(`   Esperado: "${expected}"`);
      console.log(`   Recebido: "${result}"`);
    }
  });

  console.log(`\n📊 Resultado: ${passed}/${testCases.length} testes passaram`);

  if (failed === 0) {
    console.log('✨ Todos os testes passaram com sucesso!');
  } else {
    console.log(`⚠️  ${failed} teste(s) falharam`);
  }

  // Testes adicionais
  console.log('\n🔍 Testes de validação:');
  console.log(`isValidPhase("Execução"): ${isValidPhase('Execução')}`);
  console.log(`isValidPhase("Fase Inválida"): ${isValidPhase('Fase Inválida')}`);

  console.log('\n📦 Teste getPhaseInfo:');
  const phaseInfo = getPhaseInfo('10');
  console.log(JSON.stringify(phaseInfo, null, 2));

  return failed === 0;
}

// Executar testes se for chamado diretamente
if (typeof window === 'undefined') {
  // Node.js environment
  runTests();
} else {
  // Browser environment
  window.runPhaseTests = runTests;
  console.log('💡 Execute window.runPhaseTests() no console do navegador');
}

export { runTests };
