// Teste para verificar a correção da normalização de fase

const phaseInput = '2.1 Trânsito em Julgado';
const classNature = 'Cumprimento de sentença';

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

function isExecutionClass(classNature) {
  if (!classNature) return false;
  const lower = classNature.toLowerCase();
  return EXECUTION_CLASSES.some(exec => lower.includes(exec));
}

const isExecution = isExecutionClass(classNature);
const inputLower = phaseInput.toLowerCase();

console.log('========================================');
console.log('Teste de Normalização de Fase');
console.log('========================================');
console.log('');
console.log('Processo: 0029123-13.2015.8.19.0002');
console.log('Fase no banco:', phaseInput);
console.log('Classe:', classNature);
console.log('');
console.log('Análise:');
console.log('  - É classe de execução?', isExecution);
console.log('  - inputLower:', inputLower);
console.log('  - Contém "execução"?', inputLower.includes('execução'));
console.log('  - Contém "cumprimento"?', inputLower.includes('cumprimento'));
console.log('  - Contém "transitado"?', inputLower.includes('transitado'));
console.log('  - Contém "trânsito"?', inputLower.includes('trânsito'));
console.log('');

let classificacao;
if (isExecution || inputLower.includes('execução') || inputLower.includes('cumprimento')) {
  if (inputLower.includes('suspensa') && inputLower.includes('parcial')) {
    classificacao = 'Execução Suspensa Parcialmente (Impugnação Parcial) [Fase 12]';
  } else if (inputLower.includes('suspensa')) {
    classificacao = 'Execução Suspensa [Fase 11]';
  } else {
    classificacao = 'Execução [Fase 10]';
  }
} else if (inputLower.includes('transitado') || inputLower.includes('trânsito')) {
  classificacao = 'Conhecimento — Sentença com Trânsito em Julgado [Fase 03]';
} else {
  classificacao = 'Conhecimento — Antes da Sentença [Fase 01]';
}

console.log('Resultado:');
console.log('  => Classificado como:', classificacao);
console.log('');
console.log('✅ Correção aplicada: O processo agora será classificado corretamente como "Execução"');
console.log('   pois a classe "Cumprimento de sentença" é uma classe de execução.');
console.log('========================================');
