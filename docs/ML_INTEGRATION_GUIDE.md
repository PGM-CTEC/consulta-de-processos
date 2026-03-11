# Guia de Integração com Modelos de Machine Learning

## Visão Geral

O sistema de "Consulta de Processos" inclui uma integração completa com modelos de Machine Learning para classificação automática de fases processuais. Este guia descreve como treinar, avaliar e usar os modelos.

## Arquitetura

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Analytics Endpoints                ML Endpoints            │
│  ─────────────────                ──────────────            │
│  GET /analytics/corrections/stats   POST /ml/train         │
│  GET /analytics/corrections/export  GET /ml/train          │
│  GET /analytics/phase-patterns      GET /ml/train/{id}    │
│                                     POST /ml/predict       │
│                                     POST /ml/evaluate      │
│                                                             │
│                    ↓                      ↓                 │
│          ┌──────────────────┐    ┌──────────────────┐     │
│          │  Phase Correction │    │ MLIntegration    │     │
│          │    Database      │    │   Service        │     │
│          └──────────────────┘    └──────────────────┘     │
│                                          ↓                  │
│          ┌────────────────────────────────────────┐        │
│          │   Multiple Backends Support           │        │
│          ├────────────────────────────────────────┤        │
│          │ • Local (Scikit-learn)                │        │
│          │ • Remote API                          │        │
│          │ • Hugging Face Hub                    │        │
│          └────────────────────────────────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### MLIntegrationService

Localização: `backend/services/ml_integration_service.py`

**Responsabilidades:**
- Gerenciar ciclo de vida de modelos (treino, predição, avaliação)
- Abstrair múltiplos backends (local, remote, HuggingFace)
- Rastrear jobs de treinamento
- Serializar/desserializar predições

## Endpoints de Analytics

### 1. Estatísticas de Correções
```
GET /analytics/corrections/stats
```

**Response:**
```json
{
  "total_corrections": 156,
  "unique_processes": 142,
  "phase_transitions": {
    "02->05": 89,
    "03->04": 42,
    "01->02": 25
  },
  "most_common_corrections": [
    {"transition": "02->05", "count": 89},
    {"transition": "03->04", "count": 42}
  ]
}
```

### 2. Exportar Correções (com Paginação)
```
GET /analytics/corrections/export?page=1&page_size=1000&format=jsonl
```

**Parâmetros:**
- `page`: Número da página (padrão: 1)
- `page_size`: Items por página (padrão: 1000, máximo: 10000)
- `format`: `jsonl` (padrão) ou `json`

**Response JSONL:**
```jsonl
{"process_number":"0123456-78.2020.8.19.0001","original_phase":"02","corrected_phase":"05","reason":"Encontrado trânsito em julgado","corrected_at":"2025-03-06T15:30:45.123456","corrected_by":"user@example.com"}
{"process_number":"0123457-79.2020.8.19.0002","original_phase":"03","corrected_phase":"04",...}
```

**Response JSON:**
```json
{
  "data": [
    {
      "process_number": "0123456-78.2020.8.19.0001",
      "original_phase": "02",
      "corrected_phase": "05",
      "reason": "Encontrado trânsito em julgado",
      "corrected_at": "2025-03-06T15:30:45.123456",
      "corrected_by": "user@example.com"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 1000,
    "total_corrections": 5234,
    "total_pages": 6,
    "has_next": true,
    "has_previous": false
  }
}
```

### 3. Padrões de Fase
```
GET /analytics/phase-patterns
```

**Response:**
```json
{
  "patterns": [
    {
      "original_phase": "02",
      "corrected_phase": "05",
      "count": 89,
      "reasons": {
        "Encontrado trânsito em julgado": 65,
        "Fase anterior era incorreta": 24
      },
      "processes": ["0123456-78.2020.8.19.0001", "0123457-79.2020.8.19.0002", ...]
    }
  ],
  "total_patterns": 12,
  "total_corrections": 156
}
```

## Endpoints de ML

### 1. Iniciar Treinamento
```
POST /ml/train?model_name=phase-classifier-v1
```

**Response:**
```json
{
  "job_id": "phase-classifier-v1-20260311_204513",
  "status": "completed",
  "model_version": "1.0.1",
  "created_at": "2026-03-11T20:45:13.139345",
  "total_samples": 156
}
```

**Status Codes:**
- `200`: Job criado e processado
- `400`: Parâmetros inválidos
- `500`: Erro no processamento

### 2. Listar Jobs de Treinamento
```
GET /ml/train
```

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "phase-classifier-v1-20260311_204513",
      "status": "completed",
      "model_version": "1.0.1",
      "created_at": "2026-03-11T20:45:13.139345",
      "accuracy": 0.85
    }
  ],
  "total": 5
}
```

### 3. Obter Status do Job
```
GET /ml/train/{job_id}
```

**Response:**
```json
{
  "job_id": "phase-classifier-v1-20260311_204513",
  "status": "completed",
  "model_version": "1.0.1",
  "created_at": "2026-03-11T20:45:13.139345",
  "completed_at": "2026-03-11T20:45:14.148730",
  "total_samples": 156,
  "accuracy": 0.85,
  "error": null
}
```

**Status Values:**
- `pending`: Aguardando processamento
- `training`: Em treinamento
- `completed`: Treinamento concluído com sucesso
- `failed`: Falha no treinamento

### 4. Fazer Predição
```
POST /ml/predict?process_number=0123456-78.2020.8.19.0001&original_phase=02
```

**Parâmetros:**
- `process_number`: Número do processo CNJ
- `original_phase`: Fase atual do processo
- `movements`: (opcional) Array de movimentos do processo

**Response:**
```json
{
  "process_number": "0123456-78.2020.8.19.0001",
  "predicted_phase": "05",
  "confidence": 0.87,
  "model_version": "1.0.2",
  "timestamp": "2026-03-11T20:45:16.812380"
}
```

**Interpretação:**
- `confidence`: Probabilidade da predição (0.0 a 1.0)
- `model_version`: Versão do modelo usado
- Confianças < 0.7 devem ser revisadas manualmente

### 5. Avaliar Modelo
```
POST /ml/evaluate
```

**Response:**
```json
{
  "accuracy": 0.85,
  "precision": 0.82,
  "recall": 0.88,
  "f1": 0.85,
  "samples": 156
}
```

**Métricas:**
- **Accuracy**: % de predições corretas
- **Precision**: % de predições positivas que estavam certas
- **Recall**: % de casos positivos que foram encontrados
- **F1-Score**: Média harmônica entre precision e recall

## Fluxo de Uso Recomendado

### 1. Coleta de Dados
```bash
# Exportar correções para treinamento
curl -s "http://localhost:8000/analytics/corrections/export?page=1&page_size=10000&format=jsonl" \
  > training-data.jsonl

# Verificar padrões antes de treinar
curl -s "http://localhost:8000/analytics/phase-patterns" | jq '.patterns | sort_by(.count) | reverse'
```

### 2. Treinamento
```bash
# Iniciar treinamento
JOB=$(curl -s -X POST "http://localhost:8000/ml/train?model_name=classifier-v2" | jq -r .job_id)

# Monitorar progresso
curl -s "http://localhost:8000/ml/train/$JOB" | jq .
```

### 3. Avaliação
```bash
# Avaliar modelo treinado
curl -s -X POST "http://localhost:8000/ml/evaluate" | jq .
```

### 4. Produção (Predição)
```bash
# Predizer fase para novo processo
curl -s -X POST \
  "http://localhost:8000/ml/predict?process_number=0123456-78.2020.8.19.0001&original_phase=02" \
  | jq .
```

## Backends

### Local Backend (Padrão)

```python
from backend.services.ml_integration_service import MLIntegrationService

service = MLIntegrationService(backend="local")
```

**Características:**
- ✓ Nenhuma dependência externa
- ✓ Rápido para pequenos datasets
- ✓ TODO: Implementar Scikit-learn/FastText

### Remote Backend

```python
service = MLIntegrationService(
    backend="remote",
    api_endpoint="https://ml-api.example.com",
    api_key="sk-..."
)
```

**Características:**
- ✓ Escalável para grandes datasets
- ✓ Mais poder computacional
- Requer serviço externo

### Hugging Face Backend

```python
service = MLIntegrationService(
    backend="huggingface",
    api_key="hf_..."
)
```

**Características:**
- ✓ Acesso a modelos pré-treinados
- ✓ Fine-tuning com transformers
- Requer conta Hugging Face

## Integração com ProcessDetails

Para integrar predições automáticas no frontend:

```javascript
// frontend/src/components/ProcessDetails.jsx

// Obter predição do modelo
const predictPhase = async (processNumber, originalPhase) => {
  const response = await fetch(
    `/ml/predict?process_number=${processNumber}&original_phase=${originalPhase}`,
    { method: 'POST' }
  );
  return response.json();
};

// Usar na interface
const [prediction, setPrediction] = useState(null);

useEffect(() => {
  if (data?.number && data?.phase) {
    predictPhase(data.number, data.phase).then(setPrediction);
  }
}, [data]);

// Renderizar sugestão
{prediction && (
  <div className="bg-blue-50 border border-blue-200 p-3 rounded">
    <p className="text-sm font-semibold">Sugestão do Modelo:</p>
    <p className="text-lg">Fase: {prediction.predicted_phase}</p>
    <p className="text-xs text-gray-600">Confiança: {(prediction.confidence * 100).toFixed(1)}%</p>
  </div>
)}
```

## Próximos Passos

1. **Implementar Backend Local**
   - [ ] Scikit-learn para classificação
   - [ ] FastText para embeddings de razões
   - [ ] Salvar modelos com joblib

2. **Integração Remote**
   - [ ] Configurar serviço ML externo
   - [ ] Autenticação com tokens JWT
   - [ ] Rate limiting

3. **Hugging Face**
   - [ ] Fine-tune DistilBERT em correções
   - [ ] Model card no Hub
   - [ ] Versionamento de modelos

4. **Frontend**
   - [ ] Sugestões de fase em ProcessDetails
   - [ ] Dashboard de acurácia do modelo
   - [ ] Feedback loop (user corrections)

## Troubleshooting

### Erro: "ML model unavailable"
- Backend não está respondendo
- Verifique se MLIntegrationService foi inicializado
- Confira logs em `/tmp/backend.log`

### Job stuck em "training"
- Verifique status: `GET /ml/train/{job_id}`
- Se >= 5 min, considere reiniciar backend
- Cheque logs para exceções

### Baixa accuracy
- Verifique qualidade dos dados JSONL
- Aumente `page_size` para mais samples no treinamento
- Analise padrões: `GET /analytics/phase-patterns`

## Documentação Técnica

- ML Service: `backend/services/ml_integration_service.py`
- Analytics Endpoints: `backend/main.py` (linhas 663-780)
- Models: `backend/models.py` (PhaseCorrection)
