# Plano: Edição Manual de Fase Processual com Registro de Motivo

## Contexto

O sistema de consulta processual exibe a fase atual de cada processo em 3 abas (busca individual, busca em lote, histórico). Não existe mecanismo para o usuário corrigir manualmente uma fase classificada incorretamente. A funcionalidade é necessária para:

1. Permitir que advogados retifiquem classificações erradas do modelo ML
2. Registrar pares (fase_original, fase_corrigida, motivo) para retreinamento futuro do modelo de ML de classificação

O estado atual: nenhum campo de `phase_override`, nenhum endpoint PATCH/PUT de fase, nenhum componente de edição ou modal existe. O `phase_override` em `process_service.py` linha 340 é dead code/placeholder sem utilização.

---

## Arquivos Críticos

### Backend
- `backend/models.py` — adicionar modelo `PhaseCorrection`
- `backend/schemas.py` — adicionar `PhaseCorrectionCreate` e `PhaseCorrectionResponse`
- `backend/main.py` — dois novos endpoints + auto-migração no lifespan
- `backend/constants.py` — novo arquivo com `VALID_PHASE_CODES`

### Frontend
- `frontend/src/components/PhaseEditModal.jsx` — novo componente (modal)
- `frontend/src/services/phaseCorrections.js` — novo arquivo de serviço API
- `frontend/src/components/ProcessDetails.jsx` — linhas 280–303 (badge de fase)
- `frontend/src/components/BulkSearch.jsx` — `ResultRow` (24–57) e `VirtualResultsBody` (81–158)
- `frontend/src/components/HistoryTab.jsx` — `PhaseBadge` (55–71) e bloco de item (295–297)

### Testes
- `backend/tests/test_phase_corrections.py` — novo arquivo
- `frontend/src/components/__tests__/PhaseEditModal.test.jsx` — novo arquivo
- `frontend/src/services/phaseCorrections.test.js` — novo arquivo

---

## Decisão Arquitetural: Dados Originais Intactos

A fase corrigida **nunca sobrescreve** `Process.phase` nem `SearchHistory.phase`. Razões:
- `Process.phase` é sobrescrito a cada nova consulta via DataJud/Fusion
- Para ML, o par (fase_original, fase_corrigida) só tem valor se ambos preservados
- Tabela dedicada mantém histórico auditável de todas as correções

O frontend aplica a nova fase via **optimistic update local** sem refetch.

---

## Implementação

### Passo 1 — `backend/constants.py` (novo arquivo)

```python
VALID_PHASE_CODES = {str(i).zfill(2) for i in range(1, 16)}  # "01" a "15"
```

### Passo 2 — `backend/models.py`: Novo modelo

```python
class PhaseCorrection(Base):
    __tablename__ = "phase_corrections"
    id = Column(Integer, primary_key=True, index=True)
    process_number = Column(String, nullable=False, index=True)
    original_phase = Column(String(20), nullable=True)
    corrected_phase = Column(String(20), nullable=False)
    reason = Column(Text, nullable=False)
    source_tab = Column(String(20), nullable=True)  # "single"|"bulk"|"history"
    classification_log_snapshot = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        Index('ix_phase_corrections_number', 'process_number'),
        Index('ix_phase_corrections_created_at', 'created_at'),
    )
```

Sem `SoftDeleteMixin` — correções são imutáveis. A correção mais recente por `process_number` é a vigente.

### Passo 3 — `backend/schemas.py`: Dois novos schemas

```python
class PhaseCorrectionCreate(BaseModel):
    corrected_phase: str  # validado contra VALID_PHASE_CODES, normalizado para zfill(2)
    reason: str = Field(..., min_length=10, max_length=2000)
    source_tab: Optional[str] = Field(None, pattern="^(single|bulk|history)$")
    original_phase: Optional[str] = None
    classification_log_snapshot: Optional[Any] = None

class PhaseCorrectionResponse(BaseModel):
    id: int; process_number: str; original_phase: Optional[str]
    corrected_phase: str; reason: str; source_tab: Optional[str]
    classification_log_snapshot: Optional[Any]; created_at: datetime
    class Config: from_attributes = True
    # @model_validator: deserializa classification_log_snapshot de JSON string → dict
```

### Passo 4 — `backend/main.py`: Auto-migração no lifespan

No bloco `lifespan`, após as verificações de tabela existentes:

```python
if "phase_corrections" not in existing_tables:
    models.Base.metadata.tables["phase_corrections"].create(bind=engine)
```

### Passo 5 — `backend/main.py`: Dois novos endpoints

```
POST /processes/{number}/phase-correction  → 201 PhaseCorrectionResponse
GET  /phase-corrections                    → List[PhaseCorrectionResponse]
     query params: process_number, limit (max 1000), offset
```

### Passo 6 — `frontend/src/services/phaseCorrections.js` (novo)

```javascript
export const submitPhaseCorrection = async (processNumber, data) =>
    (await api.post(`/processes/${processNumber}/phase-correction`, data)).data;

export const listPhaseCorrections = async (params = {}) =>
    (await api.get('/phase-corrections', { params })).data;
```

### Passo 7 — `frontend/src/components/PhaseEditModal.jsx` (novo)

Modal acessível (`role=dialog`, `aria-modal`, foco controlado, Escape para fechar). Props:
- `processNumber`, `currentPhase`, `classificationLog`, `sourceTab`
- `onClose()`, `onSuccess(newPhaseCode)`

Corpo do modal:
1. Fase atual (read-only badge)
2. `<select>` com 15 opções de `ALL_PHASES` ordenadas por código
3. `<textarea>` para motivo (obrigatório, mín. 10 chars, contador "N/2000")
4. Mensagem de erro inline
5. Footer: botão Cancelar + botão "Salvar Correção" (disabled enquanto submitting ou reason < 10)

Ao confirmar: chama `submitPhaseCorrection`, exibe toast de sucesso, chama `onSuccess(code)`.

### Passo 8 — `ProcessDetails.jsx`

Localização: linhas 280–303 (bloco "Fase Atual").

- Adicionar `useState(null)` para `manualPhase`
- Priorizar `manualPhase` no `useMemo` de `correctedPhase` (linha 90)
- Ícone `<Pencil>` de `lucide-react` ao lado do badge (já importado no projeto)
- Badge `"Corrigida"` em violeta quando `manualPhase !== null`
- Renderizar `<PhaseEditModal>` quando `showPhaseEdit === true`

### Passo 9 — `BulkSearch.jsx`

Estratégia: elevar estado de correções ao componente pai.

- `useState({})` para `phaseCorrections` (chave: `result.number`) e `editingProcess`
- Passar `correctedPhase={phaseCorrections[result.number] ?? null}` e `onEditPhase` para `ResultRow`
- Replicar mesma lógica no `VirtualResultsBody` (atenção: `estimateSize` pode precisar aumentar de 60→72 se o botão quebrar linha)
- Usar `useCallback` para `handleEditPhase` (evitar re-render do `React.memo`)

### Passo 10 — `HistoryTab.jsx`

- Estado `phaseCorrections` keyed por `item.id` (não `item.number` — mesmo número pode aparecer múltiplas vezes no histórico)
- Modificar `PhaseBadge` para aceitar prop `corrected={bool}` e exibir badge adicional
- Botão `<Pencil>` ao lado do `<PhaseBadge>` com `e.stopPropagation()`
- Modal renderizado ao final do componente

---

## Ordem de Execução

| Passo | Arquivo | Depende de |
|-------|---------|-----------|
| 1 | `backend/constants.py` | — |
| 2 | `backend/models.py` | — |
| 3 | `backend/schemas.py` | 1, 2 |
| 4–5 | `backend/main.py` | 3 |
| 6 | `frontend/src/services/phaseCorrections.js` | 5 |
| 7 | `frontend/src/components/PhaseEditModal.jsx` | 6 |
| 8–10 | `ProcessDetails`, `BulkSearch`, `HistoryTab` | 7 |
| 11 | Testes | 1–10 |

---

## Verificação

### Backend
```bash
cd "c:\Projetos\Consulta processo"
python -m pytest backend/tests/test_phase_corrections.py -v
python -m pytest backend/tests/ -v  # suite completa — verificar sem regressões
```

### Frontend
```bash
cd frontend
npx vitest run --reporter=verbose
```

### Manual E2E
1. Iniciar com `iniciar.bat`
2. Buscar um processo → clicar no ícone de lápis ao lado da fase → selecionar nova fase + motivo → confirmar
3. Verificar badge "Corrigida" e nova fase exibida
4. Ir para aba de histórico → verificar se o mesmo processo mostra o botão de edição
5. Ir para busca em lote → buscar múltiplos processos → verificar botão de edição em cada linha
6. `GET http://localhost:8000/phase-corrections` → verificar que a correção aparece na listagem
