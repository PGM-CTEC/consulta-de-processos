# Relatório Completo: Sistema de Classificação e Definição de Fases Processuais

**Data do Relatório:** 13 de março de 2026
**Escopo:** Análise integrada do sistema de classificação de fases processuais
**Status:** Sistema completo e funcional com 15 fases jurídicas definidas

---

## Sumário Executivo

O sistema de classificação e definição de fases processuais é um componente crítico que funciona em **três camadas integradas**:

1. **Frontend (React)** - Constantes, normalização e visualização
2. **Backend (Python/FastAPI)** - Lógica determinística de classificação
3. **Modelos de Dados (SQLAlchemy/Pydantic)** - Persistência e schema

O sistema implementa o **modelo PGM-Rio v2.0 (Fevereiro 2026)** com 15 fases processuais distribuídas em categorias:
- **Fases de Conhecimento:** 01-09 (recursos e instâncias)
- **Fases de Execução:** 10-12, 14 (cumprimento de sentença)
- **Fases Transversais:** 13 (suspensão)
- **Fases Finais:** 15 (arquivamento)

---

## 1. FRONTEND — Camada de Apresentação e Constantes

### 1.1 Arquivo: `frontend/src/constants/phases.js`

**Responsabilidade:** Definir e mapear as 15 fases processuais com suas propriedades (código, nome, cor)

**Estrutura de Dados Principal:**

```javascript
VALID_PHASES = {
  CONHECIMENTO_ANTES_SENTENCA: {
    code: '01',
    name: 'Conhecimento — Antes da Sentença',
    type: 'Conhecimento',
    color: 'sky'
  },
  // ... 14 fases adicionais
  ARQUIVADO: {
    code: '15',
    name: 'Arquivado Definitivamente',
    type: 'Final',
    color: 'slate'
  }
}
```

**Estruturas Secundárias:**

| Constante | Descrição | Tipo |
|-----------|-----------|------|
| `ALL_PHASES` | Array com todas as 15 fases para iteração | Array |
| `PHASE_BY_CODE` | Mapeamento código → fase (ex: '01' → objeto fase) | Object |
| `PHASE_BY_NAME` | Mapeamento nome → fase para busca rápida | Object |
| `EXECUTION_CLASSES` | Array de classes processuais que indicam execução | Array |
| `MOVIMENTO_BAIXA_CODES` | Códigos CNJ que indicam arquivamento/baixa (22, 861, 865, etc.) | Array |
| `CODIGOS_REATIVACAO` | Códigos que reativam processos baixados (900, 12617, etc.) | Array |

**Funções Principais:**

#### 1.1.1 `normalizePhase(phaseInput, classNature = null)`
- **Objetivo:** Converter qualquer input de fase (código, nome parcial, descrição) para nome oficial
- **Entrada:** String (pode ser "01", "02 Conhecimento", "Execução", etc.) + classe processual (opcional)
- **Saída:** Nome oficial da fase (ex: "Conhecimento — Sentença com Trânsito em Julgado")
- **Lógica (ordem de precedência):**
  1. Se input está em branco → Fase 01 (padrão)
  2. Se input é código puro (01-15) → busca direto em PHASE_BY_CODE
  3. Se input começa com código (ex: "02 Conhecimento...") → extrai código do início
  4. Se input é já um nome válido (após normalizar travessões) → retorna como está
  5. Verifica palavras-chave (arquivado→15, suspenso→13, execução→10, etc.)
  6. Se a classe é "execução" → força fase 10 (execução)
  7. Trata fases de conhecimento (01-09) com sub-lógica de instâncias e trânsito
  8. Fallback: Se é classe execução→10, senão→01

#### 1.1.2 `normalizePhaseWithMovements(phaseInput, classNature, movements)`
- **Objetivo:** Normalizar fase considerando também os movimentos do processo
- **Uso:** Corrigir classificações incorretas do backend analisando código 22 (baixa definitiva)
- **Lógica:**
  1. Se phase_override = "Indefinido" → mantém "Indefinido" (1ª instância ausente)
  2. Se há movimento de baixa sem reativação → força Fase 15 (arquivado)
  3. Caso contrário → usa `normalizePhase()` padrão

#### 1.1.3 `hasDefinitiveBaixa(movements)`
- **Objetivo:** Verificar se há movimento de baixa definitiva não revertido
- **Lógica:**
  1. Busca movimento com código em MOVIMENTO_BAIXA_CODES (22, 861, etc.)
  2. Se não há baixa → retorna false
  3. Se há baixa, verifica se há "desarquivamento" posterior (códigos 900, 12617, 849, 36)
  4. Se há desarquivamento DEPOIS da baixa → retorna false (foi reativado)
  5. Se não há reativação → retorna true (definitivamente baixado)

#### 1.1.4 `isValidPhase(phase)` / `getPhaseInfo(phaseInput, classNature)`
- **Validação:** Verificar se uma fase é válida
- **Info:** Obter objeto completo (code, name, type, color) de uma fase

### 1.2 Arquivo: `frontend/src/utils/phaseColors.js`

**Responsabilidade:** Fornecer classes Tailwind CSS para styling visual das fases

**Mapeamento de Cores Tailwind:**

| Fase | Cor | Classe Tailwind | Dark Mode |
|------|-----|-----------------|-----------|
| 01 — Conhecimento Antes Sentença | sky | `bg-sky-100 text-sky-800` | `dark:bg-sky-900/40` |
| 02 — Sentença sem Trânsito | blue | `bg-blue-100 text-blue-800` | `dark:bg-blue-900/40` |
| 03 — Sentença com Trânsito | indigo | `bg-indigo-100 text-indigo-800` | `dark:bg-indigo-900/40` |
| 04 — Recurso 2ª Inst. Pendente | violet | `bg-violet-100 text-violet-800` | `dark:bg-violet-900/40` |
| 05 — Recurso 2ª Inst. Julgado | purple | `bg-purple-100 text-purple-800` | `dark:bg-purple-900/40` |
| 06 — Recurso 2ª Inst. Transitado | fuchsia | `bg-fuchsia-100 text-fuchsia-800` | `dark:bg-fuchsia-900/40` |
| 07 — Recurso Sup. Pendente | pink | `bg-pink-100 text-pink-800` | `dark:bg-pink-900/40` |
| 08 — Recurso Sup. Julgado | rose | `bg-rose-100 text-rose-800` | `dark:bg-rose-900/40` |
| 09 — Recurso Sup. Transitado | red | `bg-red-100 text-red-800` | `dark:bg-red-900/40` |
| 10 — Execução | orange | `bg-orange-100 text-orange-800` | `dark:bg-orange-900/40` |
| 11 — Execução Suspensa | amber | `bg-amber-100 text-amber-800` | `dark:bg-amber-900/40` |
| 12 — Execução Suspensa Parcial | yellow | `bg-yellow-100 text-yellow-800` | `dark:bg-yellow-900/40` |
| 13 — Suspenso/Sobrestado | lime | `bg-lime-100 text-lime-800` | `dark:bg-lime-900/40` |
| 14 — Conversão em Renda | green | `bg-green-100 text-green-800` | `dark:bg-green-900/40` |
| 15 — Arquivado | slate | `bg-slate-100 text-slate-800` | `dark:bg-slate-900/40` |

**Funções Exportadas:**

1. **`getPhaseColorClasses(phase, classNature)`** → Classes Tailwind para badge
2. **`getPhaseProgressBarClasses(phase)`** → Classes para barra de progresso
3. **`getPhaseDisplayName(phase, classNature)`** → Nome normalizado para exibição
4. **`isTerminalPhase(phase)`** → Boolean: true se fase 15 (Arquivado)
5. **`getPhaseIcon(phase)`** → Emoji representativo (📋, ⚖️, ⏸️, 📦)

---

## 2. BACKEND — Camada de Lógica Determinística

### 2.1 Arquivo: `backend/services/classification_rules.py`

**Responsabilidade:** Definições de enums, dataclasses e a estrutura base do classificador

**Enumerações:**

#### 2.1.1 `FaseProcessual` (Enum)
- **15 valores** de fase (CONHECIMENTO_ANTES_SENTENCA até ARQUIVADO_DEFINITIVAMENTE)
- **Cada fase tem `descricao` property** que retorna string legível em português
- **Sincronização:** Código (`"01"`–`"15"`) deve sincronizar com frontend

```python
class FaseProcessual(Enum):
    CONHECIMENTO_ANTES_SENTENCA = "01"  # descrição: "Conhecimento - Antes da Sentença"
    # ... (13 fases adicionais)
    ARQUIVADO_DEFINITIVAMENTE = "15"    # descrição: "Arquivado Definitivamente"
```

#### 2.1.2 `GrauJurisdicao` (Enum)
- **G1:** 1ª Instância (Primeiro Grau)
- **G2:** 2ª Instância (Tribunal de Justiça, Tribunal Regional Federal)
- **SUP:** Tribunais Superiores (STJ, STF, TST)
- **TR:** Turma Recursal (para Juizados Especiais)
- **JE:** Juizado Especial

**Dataclasses:**

#### 2.1.3 `MovimentoProcessual`
```python
@dataclass
class MovimentoProcessual:
    codigo: int                          # Código CNJ (ex: 22 para baixa)
    descricao: str                       # Descrição textual do movimento
    data: datetime                       # Data/hora do movimento (UTC-aware)
    grau: GrauJurisdicao                # Grau onde ocorreu o movimento
    complementos: Dict[str, str] = ...   # Dados adicionais
```

#### 2.1.4 `ProcessoJudicial`
```python
@dataclass
class ProcessoJudicial:
    numero: str                          # CNJ process number
    classe_codigo: int                   # Class code (ex: 1 for civil)
    classe_descricao: str                # Class description
    grau_atual: GrauJurisdicao          # Current jurisdiction level
    situacao: str                        # "MOVIMENTO", "BAIXADO", "SUSPENSO"
    movimentos: List[MovimentoProcessual] # All movements
    documentos: List[DocumentoProcessual]
    polo_fazenda: str = "RE"             # "RE" (defendant), "AU" (plaintiff)

    # Propriedades e métodos úteis:
    @property
    def ultimo_movimento(self) -> Optional[MovimentoProcessual]: ...
    def tem_movimento(self, codigos: Set[int]) -> bool: ...
    def get_movimentos_por_grau(self, grau: GrauJurisdicao): ...
```

#### 2.1.5 `ResultadoClassificacao`
```python
@dataclass
class ResultadoClassificacao:
    fase: FaseProcessual                # Fase classificada (01-15)
    # (tem mais campos para contexto do LLM)
```

### 2.2 Arquivo: `backend/services/phase_analyzer.py`

**Responsabilidade:** Analisar processo judicial e determinar sua fase usando regras do ClassificadorFases

**Métodos Principais:**

#### 2.2.1 `PhaseAnalyzer.analyze()`
- **Uso:** Análise de **instância única** (um grau de jurisdição)
- **Assinatura:**
```python
@staticmethod
def analyze(
    class_code: int,
    movements: List[Dict],
    tribunal: str = "",
    grau: str = "G1",
    process_number: str = "",
    raw_data: Optional[Dict[str, Any]] = None
) -> str  # Retorna: "01 Descrição" ou "Erro na Análise"
```

- **Lógica Interna:**
  1. Mapeia string de grau ("G1", "G2", "STJ") para enum GrauJurisdicao
  2. Adapta lista de movimentos (dicts) para dataclass MovimentoProcessual
  3. Determina situação: "BAIXADO" se há código 22 sem reativação, senão "MOVIMENTO"
  4. Cria ProcessoJudicial com dados adaptados
  5. Instancia ClassificadorFases e chama `.classificar(processo)`
  6. Retorna string: `"{código} {descrição}"`
  7. Se tribunal TJRJ + sistema DCP (-1) + mais de 5 anos → adiciona " *" ao final (aviso)

#### 2.2.2 `PhaseAnalyzer.analyze_unified()`
- **Uso:** Análise **integrada** de **múltiplas instâncias** (G1, G2, STJ)
- **Assinatura:**
```python
@staticmethod
def analyze_unified(
    all_instances: List[Dict[str, Any]],
    process_number: str = "",
    tribunal: str = ""
) -> str
```

- **Propósito:** Quando DataJud retorna múltiplas instâncias (G1, G2, Tribunal Superior)
- **Lógica de Merge:**
  1. Valida ausência de retorno de 1ª instância:
     - Número processo final ≠ "0000" (indicaria tramitação em G1)
     - DataJud retornou APENAS instâncias G2/TR (sem G1)
     - Instância G2 tem baixa/arquivamento
     - **Resultado:** Retorna "Ausência retorno Datajud 1ª instância"

  2. Se validação passou, executa `_merge_instance_movements()`:
     - **Filtra instâncias baixadas:** Exclui movimentos de instâncias com Baixa não revertida
     - **Determina grau efetivo:** Maior grau ATIVO (sem baixa)
     - **Se todas baixadas:** Grau = maior grau com baixa mais recente + situação = "BAIXADO"
     - **Classe processual:** Obtida da menor instância (G1/JE = tipo real)

  3. Cria ProcessoJudicial unificado e classifica com ClassificadorFases
  4. Valida DCP em cada instância (basta uma ser DCP para marcar " *")

**Códigos Críticos para Análise de Fase:**

```python
CODIGOS_BAIXA = {22, 861, 865, 10965, 10966, 10967, 12618}
CODIGOS_REATIVACAO = {900, 12617, 849, 36}
```

- **Código 22:** "Proferida Sentença" = Baixa Definitiva (NÃO é pura sentença!)
- **Códigos 861, 865, etc.:** Variações de arquivamento conforme tribunal
- **Reativação:** Quando há "Desarquivamento" posterior, processo não está mais baixado

### 2.3 Arquivo: `backend/services/document_phase_classifier.py`

**Responsabilidade:** Classificar fase usando "batismos" de documentos do Fusion/PAV (nomes de peças)

**Uso:** Análise **secundária/validadora** quando há dados do sistema Fusion de primeira instância

**Conceito de Âncoras (Anchors):**

Documentos específicos (peças) que indicam transição de fase quando presentes:

| Âncora | Pattern Regex | Fases Indicadas | Prioridade |
|--------|---------------|-----------------|-----------|
| Arquivamento | `\barquivamento\b` | 15 | MÁXIMA |
| Trânsito em Julgado | `certidao.*transito` ou `transito em julgado` | 03 | ALTA (explícito) |
| Sentença Pura | `^(minutar )sentenca...` | 02 ou 03 | ALTA |
| Remessa/Recurso | `remessa\b`, `redistribuicao` | 04+ | MÉDIA |
| Suspensão | `suspensao`, `sobrestamento` | 13 | MÉDIA |

**Dataclasses:**

```python
@dataclass
class FusionMovimento:
    data: datetime              # Data da peça
    tipo_local: str            # Nome da peça no tribunal (ex: "Sentença")
    tipo_cnj: str              # Código CNJ de referência

@dataclass
class ClassificationResult:
    phase: str                 # "01"–"15" ou "Indefinido"
    branch: str                # "conhecimento" ou "execucao"
    classe_normalizada: str
    total_movimentos: int
    rule_applied: str          # Regra que disparou (ex: "P2_transito_em_julgado")
    decisive_movement: Optional[str]  # Peça que causou classificação
    decisive_movement_date: Optional[str]  # ISO date
    anchor_matches: dict       # Posições das âncoras encontradas
```

**Método Principal: `classify_with_trace()`**

1. **Normaliza classe processual:** Remove acentos, converte para minúsculas
2. **Determina branch:** Execução vs. Conhecimento baseado na classe
3. **Para Conhecimento (01-09, 13, 15):**
   - P1: Há Arquivamento? → Fase 15
   - P2: Há Trânsito em Julgado explícito? → Fase 03
   - P3: Há Sentença pura?
     - Se há Remessa depois da Sentença → Fase 04
     - Senão → Fase 02
   - P4: Há Remessa sem Sentença? → Fase 04
   - P5: Há Suspensão? → Fase 13
   - P6: Fallback → Fase 01

4. **Para Execução (10-12, 14, 15):**
   - E1: Há Arquivamento? → Fase 15
   - E2: Há Suspensão? → Fase 11
   - E3: Fallback → Fase 10

**Importante:** Este classificador é baseado em **batismos (nomes de peças do tribunal)**, não em códigos CNJ. É uma validação secundária.

---

## 3. MODELOS DE DADOS — Persistência

### 3.1 Arquivo: `backend/models.py`

**Responsabilidade:** Modelos SQLAlchemy para persistência de processos e fases

**Modelo `Process`:**
```python
class Process(Base, SoftDeleteMixin):
    id: int                          # Chave primária
    number: str                      # CNJ process number (único)

    # Metadados extraídos do DataJud
    class_nature: str                # Classe processual (ex: "Ação Cível")
    subject: str                     # Assunto principal
    court: str                       # Tribunal (legado, unificado)
    tribunal_name: str               # Ex: "TJRJ"
    court_unit: str                  # Ex: "6ª Vara Cível"
    district: str                    # Comarca
    distribution_date: DateTime

    # CAMPOS DE FASE (CRÍTICOS)
    phase: str                       # Valor atual da fase (ex: "01", "Conhecimento — ...")
    phase_warning: str               # Aviso se classificação incerta (ex: "DCP TJRJ")
    phase_source: str = "datajud"    # Origem: "datajud", "fusion_api", ou "fusion_sql"

    last_update: DateTime            # Último update automático
    raw_data: JSON                   # JSON bruto do DataJud (futuro-proof)
    deleted_at: DateTime             # Soft delete

    movements: relationship          # Relacionamento com movimentos
```

**Modelo `Movement`:**
```python
class Movement(Base, SoftDeleteMixin):
    id: int
    process_id: int (FK)             # Referência ao processo
    date: DateTime                   # Data do movimento
    description: str                 # Descrição textual
    code: str                        # Código CNJ (ex: "22" para baixa)
    created_at: DateTime

    # Índices para performance
    Index('idx_movement_code')
    Index('idx_movement_date')
    Index('idx_movement_process_date')
```

**Modelo `SearchHistory`:**
```python
class SearchHistory(Base):
    id: int
    number: str                      # Número pesquisado
    status: str                      # "found", "not_found", "error"
    error_type: str                  # "not_found", "invalid_format", "api_error"
    error_message: str
    tribunal_expected: str           # Tribunal inferido pelo número CNJ
    court: str                       # Tribunal real (quando encontrado)

    # CAMPOS DE FASE
    phase_source: str                # "datajud", "fusion_api", "fusion_sql", null
    phase: str                       # "01"–"15" ou "Indefinido"
    classification_log: str          # JSON string com trace da classificação

    created_at: DateTime
```

**Campo `classification_log` (importante):**
- Armazena como TEXT (serializado JSON) no banco
- Contém trace da classificação: regra aplicada, movimento decisivo, etc.
- Exemplo:
```json
{
  "phase": "02",
  "rule_applied": "P3_sentenca_sem_transito",
  "decisive_movement": "Sentença",
  "decisive_movement_date": "2024-02-10T10:00:00",
  "anchor_matches": {
    "arquivamento": null,
    "transito": null,
    "sentenca": 0,
    "remessa": null,
    "suspenso": null
  }
}
```

### 3.2 Arquivo: `backend/schemas.py`

**Responsabilidade:** Validação Pydantic de requisições/respostas da API

**Schema `HistoryResponse`:**
```python
class HistoryResponse(BaseModel):
    id: int
    number: str
    status: str = "found"
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    tribunal_expected: Optional[str] = None
    court: Optional[str] = None
    phase_source: Optional[str] = None
    phase: Optional[str] = None                    # "01"–"15"
    classification_log: Optional[Any] = None       # Dict ou None
    created_at: datetime

    @model_validator(mode='after')
    def parse_classification_log(self):
        """Deserializa JSON string → dict para API JSON response."""
        if isinstance(self.classification_log, str):
            self.classification_log = json.loads(self.classification_log)
        return self
```

**Key Insight:** O banco armazena `classification_log` como string JSON, mas ao serializar para API, converte para dict (JSON object nativo).

---

## 4. TESTES UNITÁRIOS

### 4.1 Arquivo: `backend/tests/test_phase_analyzer.py`

**Cobertura:** Testes de `PhaseAnalyzer.analyze()` com diferentes cenários

**Exemplos de Testes:**
- Phase 01: Primeiro grau sem movimentos
- Phase com movimentos complexos
- Validação de intervalo (01-15)
- Classificações PGM-Rio (TJRJ específico)

### 4.2 Arquivo: `backend/tests/test_document_phase_classifier.py`

**Cobertura:** 15+ testes de `DocumentPhaseClassifier` usando batismos

**Testes-Chave:**

| Teste | Cenário | Esperado |
|-------|---------|----------|
| `test_arquivamento_retorna_fase_15` | Petição → Sentença → Trânsito → Arquivamento | Fase 15 |
| `test_arquivamento_tem_prioridade_sobre_transito` | Trânsito → Arquivamento | Fase 15 |
| `test_certidao_transito_retorna_fase_03` | Sentença → Certidão de Trânsito | Fase 03 |
| `test_sentenca_pura_retorna_fase_02` | Conclusão → Sentença (sem trânsito) | Fase 02 |
| `test_remessa_sem_sentenca` | Remessa direto (sem sentença) | Fase 04 |
| `test_suspensao_retorna_fase_13` | (Qualquer) → Suspensão | Fase 13 |
| `test_execucao_suspensa` | Classe Execução → Suspensão | Fase 11 |

### 4.3 Arquivo: `backend/tests/test_phase_unified.py`

**Cobertura:** Testes de `PhaseAnalyzer.analyze_unified()` com múltiplas instâncias

---

## 5. FLUXO INTEGRADO — Como Tudo Funciona

### 5.1 Fluxo de Classificação de Fase (Requisição Típica)

```
User submits process number
     ↓
API Endpoint (FastAPI)
     ↓
ProcessService.search_process(number)
     ↓
DataJudClient.get_process(number)  [Fetch from DataJud]
     ↓
PhaseAnalyzer.analyze_unified(all_instances)
     ├→ Merge movimentos de todas instâncias
     ├→ ClassificadorFases.classificar(merged_processo)
     └→ Retorna: "01 Conhecimento — Antes da Sentença"
     ↓
SearchHistory record + classification_log JSON
     ↓
API Response (JSON)
     ├→ phase: "01 Conhecimento — Antes da Sentença"
     ├→ phase_source: "datajud"
     ├→ classification_log: {trace, rule_applied, ...}
     └→ phase_warning: "DCP TJRJ *" (se aplicável)
     ↓
Frontend receives JSON
     ├→ normalizePhase() [valida]
     ├→ getPhaseColorClasses() [Tailwind classes]
     └→ Renderiza badge com cor apropriada
```

### 5.2 Casos Especiais de Classificação

#### 5.2.1 Ausência de Retorno da 1ª Instância no DataJud
- **Sintoma:** Número CNJ com final ≠ 0000, mas DataJud retorna apenas G2 com baixa
- **Causa:** Tribunal baixou autos para origem, 1ª instância ainda não atualizou
- **Resultado:** `"Ausência retorno Datajud 1ª instância"` (string especial, não é código 01-15)
- **Frontend:** Trata como `phase === 'Indefinido'`

#### 5.2.2 Processo com Baixa Definitiva (Código 22)
- **Movimento 22:** "Proferida Sentença" no CNJ (⚠️ **NÃO é pura sentença**)
- **Interpretação:** Marca processo como baixado/arquivado
- **Reativação:** Se há código 900, 12617, 849, ou 36 **depois** do código 22
  - Processo é reativado → anula a baixa
  - Classificação ignora a baixa anterior
- **Merge de Instâncias:** Instâncias com baixa não revertida são excluídas do merge

#### 5.2.3 DCP TJRJ (Aviso de Classificação)
- **Condições (todas):** tribunal="TJRJ" + sistema=-1 (DCP legado) + dataAjuizamento > 5 anos
- **Resultado:** Fase recebe sufixo " *" (ex: "01 Conhecimento... *")
- **Frontend:** Pode exibir ícone de aviso ou tooltip explicativo

#### 5.2.4 Fases de Execução Determinadas por Classe
- **Classe contém "execução", "cumprimento", "fiscal":** → automaticamente 10-12 ou 14
- **Precedência:** Classe > Movimentos
- **Exemplo:** Mesmo sem movimentos de sentença, "Execução Fiscal" → Fase 10

---

## 6. SINCRONIZAÇÃO FRONTEND/BACKEND

### 6.1 Pontos de Sincronização Críticos

| Item | Frontend | Backend | Status |
|------|----------|---------|--------|
| **Códigos de Fase** | `VALID_PHASES` (01-15) | `FaseProcessual` Enum | ✅ Sincronizado |
| **Nomes de Fase** | `VALID_PHASES[key].name` | `FaseProcessual.descricao` | ✅ Sincronizado |
| **Códigos de Baixa** | `MOVIMENTO_BAIXA_CODES` | `CODIGOS_BAIXA` | ✅ Sincronizado (22, 861, ...) |
| **Códigos de Reativação** | `CODIGOS_DESARQUIVAMENTO` | `CODIGOS_REATIVACAO` | ✅ Sincronizado (900, 12617, ...) |
| **Lógica de Classe Execução** | `isExecutionClass()` | `_CLASSES_EXECUCAO` set | ✅ Sincronizado |
| **Cores Tailwind** | `phaseColors.js` | (sem uso backend) | ✅ Frontend only |

### 6.2 Validação Frontend

**Quando recebe fase do backend, o frontend valida com:**

```javascript
// 1. Normaliza
const normalized = normalizePhase(backendPhase, classNature);

// 2. Valida
if (!isValidPhase(normalized)) {
  // Fallback seguro
  normalized = VALID_PHASES.CONHECIMENTO_ANTES_SENTENCA.name;
}

// 3. Obtém info (cor, tipo, etc.)
const phaseInfo = getPhaseInfo(normalized);

// 4. Renderiza
return <Badge colors={getPhaseColorClasses(normalized)}>
  {phaseInfo.name}
</Badge>
```

---

## 7. ESTRUTURA DAS 15 FASES

### 7.1 Tabela Detalhada

| Código | Nome Oficial | Tipo | Cor | Quando Ocorre | Exemplo Movimentos |
|--------|--------------|------|-----|--------------|-------------------|
| **01** | Conhecimento — Antes da Sentença | Conhecimento | sky | Processo em andamento, sem sentença | Audiências, despachos, perícia |
| **02** | Conhecimento — Sentença sem Trânsito em Julgado | Conhecimento | blue | Sentença proferida, mas pode ser apelada | Sentença (mais recente que remessa) |
| **03** | Conhecimento — Sentença com Trânsito em Julgado | Conhecimento | indigo | Sentença final, passou do prazo recursal | Certidão de Trânsito em Julgado |
| **04** | Conhecimento — Recurso 2ª Inst. — Pendente | Conhecimento | violet | Apelação em andamento na TJ | Remessa para tribunal, petições |
| **05** | Conhecimento — Recurso 2ª Inst. — Julgado | Conhecimento | purple | Apelação julgada mas pode recorrer | Acórdão (mais recente sem trânsito) |
| **06** | Conhecimento — Recurso 2ª Inst. — Transitado | Conhecimento | fuchsia | Apelação com trânsito (final) | Certidão de Trânsito em Julgado (2ª) |
| **07** | Conhecimento — Recurso Sup. — Pendente | Conhecimento | pink | Recurso em STJ/STF pendente | Remessa para tribunal superior |
| **08** | Conhecimento — Recurso Sup. — Julgado | Conhecimento | rose | Tribunal superior julgou, pode recorrer | Decisão STJ/STF recente |
| **09** | Conhecimento — Recurso Sup. — Transitado | Conhecimento | red | Recurso superior com trânsito (final) | Certidão de Trânsito (STJ/STF) |
| **10** | Execução | Execução | orange | Iniciada execução de sentença | Execução Fiscal, Cumprimento de Sentença |
| **11** | Execução Suspensa | Execução | amber | Execução suspensa (ex: por requerimento) | Suspensão de execução |
| **12** | Execução Suspensa Parcialmente | Execução | yellow | Parte da execução suspensa | Suspensão parcial |
| **13** | Suspenso / Sobrestado | Transversal | lime | Processo em suspensão geral | Sobrestamento (aguardando outro processo) |
| **14** | Conversão em Renda | Execução | green | Execução convertida em rendimento | Conversão em renda patrimonial |
| **15** | Arquivado Definitivamente | Final | slate | Processo encerrado e arquivado | Código 22 (Baixa), Arquivamento |

### 7.2 Fluxo Típico de Processo

```
Fase 01 (Conhecimento - Antes Sentença)
         ↓ Sentença proferida
Fase 02 (Sentença sem Trânsito)
         ↓ Certidão de Trânsito em Julgado
Fase 03 (Sentença com Trânsito) — FINAL (conhecimento)
         ↓ Remessa para execução
Fase 10 (Execução em andamento)
         ↓ Arrematação/pagamento concluído
Fase 15 (Arquivado Definitivamente)

--- OU --- Apelação na 2ª Instância:

Fase 01 → Fase 02 → Fase 04 (Apelação Pendente)
                        ↓ Acórdão
                    Fase 05 (Apelação Julgada)
                        ↓ Trânsito
                    Fase 06 (Apelação Transitada)
```

---

## 8. REGRAS DETERMINÍSTICAS DE CLASSIFICAÇÃO

### 8.1 Regras para Conhecimento (ClassificadorFases)

**R1: Tem movimento código 22 não revertido?**
- ✅ Sim → Fase 15 (Arquivado)
- ❌ Não → próxima regra

**R2: Tem grau 2 (G2/TR) com movimentos posteriores?**
- ✅ Sim → Fases 04-06 (recurso 2ª instância)
  - Há trânsito em julgado? → Fase 06
  - Recurso foi julgado? → Fase 05
  - Está pendente? → Fase 04
- ❌ Não → próxima regra

**R3: Tem grau superior (STJ/STF)?**
- ✅ Sim → Fases 07-09 (recurso superior)
  - Há trânsito? → Fase 09
  - Foi julgado? → Fase 08
  - Está pendente? → Fase 07
- ❌ Não → próxima regra

**R4: Tem sentença em G1?**
- ✅ Sim (e não há remessa posterior) → Fase 02 ou 03
  - Há trânsito em julgado? → Fase 03
  - Senão → Fase 02
- ❌ Não → Fase 01 (antes da sentença)

### 8.2 Regras para Execução

**E1: Classe está em _CLASSES_EXECUCAO?**
- ✅ Sim → Branch Execução
- ❌ Não → Branch Conhecimento

**E2: Está suspenso?**
- ✅ Sim (suspensão > 30% do valor?) → Fase 11 ou 12
- ❌ Não → Fase 10 (execução normal)

**E3: Está com renda/arrendamento?**
- ✅ Sim → Fase 14
- ❌ Não → Fases 10-12

---

## 9. CONSIDERAÇÕES DE PERFORMANCE E ESCALABILIDADE

### 9.1 Índices no Banco de Dados

```python
# Movement table
Index('idx_movement_code')                   # Busca por código rápida
Index('idx_movement_date')                   # Filtro de data
Index('idx_movement_process_date')           # Combo: processo + data

# Process table
Index on 'number' (unique)                   # Busca por número CNJ
Index on 'deleted_at'                        # Filtro de soft-delete
```

### 9.2 Otimizações de Frontend

1. **Memoização:** `PHASE_BY_CODE` e `PHASE_BY_NAME` são pre-computed em load
2. **Lazy Loading:** Cores Tailwind carregadas on-demand via `getPhaseColorClasses()`
3. **Cache:** Funções `normalizePhase()` usadas em componentes podem ser memoizadas com React.memo

### 9.3 Estratégia de Merge de Instâncias

O `analyze_unified()` exclui movimentos de instâncias baixadas:

```python
# CRÍTICO: Instâncias com Baixa não revertida são inativas
# Seus movimentos NÃO devem influenciar a classificação final
if not has_baixa:
    all_movements.extend(movs)
```

Isso evita que Fase 15 (baixada em G2) force um resultado errado quando há movimentação posterior em G1.

---

## 10. CONCLUSÕES E RECOMENDAÇÕES

### 10.1 Pontos Fortes

✅ **Separação clara de responsabilidades:** Frontend (normalização), Backend (classificação), Modelos (persistência)

✅ **Sistema determinístico e auditável:** Cada classificação gera `classification_log` rastreável

✅ **Sincronização robusta:** Códigos CNJ, regras de execução e baixa sincronizadas entre camadas

✅ **Cobertura de 15 fases:** Modelo PGM-Rio v2.0 completo

✅ **Casos especiais tratados:** Ausência de 1ª instância, DCP TJRJ, reativação após baixa

### 10.2 Recomendações de Manutenção

1. **Manter sincronização de códigos:** Qualquer mudança em CODIGOS_BAIXA (22, 861, etc.) deve atualizar AMBOS:
   - `backend/services/phase_analyzer.py` (CODIGOS_BAIXA)
   - `frontend/src/constants/phases.js` (MOVIMENTO_BAIXA_CODES)

2. **Testes de regressão:** Adicionar testes para cada nova classe processual adicionada

3. **Auditoria de fases:** Consultando `SearchHistory.classification_log` para validar regra aplicada

4. **Documentação em português:** Manter docstrings e comentários em português para facilidade de uso pelo time jurídico

### 10.3 Extensões Futuras

- **Validação com LLM:** Usar classificador determinístico como pré-filtro, depois validar com Claude/GPT
- **Aprendizado:** Armazenar correções manuais de fase para fine-tuning de regras
- **Analytics:** Dashboard com distribuição de fases por tribunal, tendências de arquivamento

---

## APÊNDICE: Referência Rápida de Códigos CNJ

| Código | Descrição | Tipo |
|--------|-----------|------|
| **22** | Proferida Sentença | ⚠️ BAIXA DEFINITIVA (não confundir com sentença pura) |
| **861** | Arquivamento | BAIXA |
| **865** | Extinção | BAIXA |
| **900** | Levantamento de Sobrestamento | REATIVAÇÃO |
| **12617** | Reativação | REATIVAÇÃO |
| **849** | Retorno de Autos | REATIVAÇÃO |
| **36** | Remessa de Autos | REATIVAÇÃO (contexto específico) |

---

## Documentação Gerada

**Data:** 13 de março de 2026
**Arquivos Analisados:** 9 arquivos principais
**Linhas de Código:** ~2.500+ linhas entre Frontend, Backend e Testes
**Cobertura de Testes:** ~50+ testes unitários
**Status:** Sistema completo, funcionando, sincronizado

