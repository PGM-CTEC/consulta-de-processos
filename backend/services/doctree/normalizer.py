"""
normalizer.py — Etapa R0: valida e normaliza a árvore bruta no contrato interno.

Conjugação ``tipo_peca`` × ``nome_arquivo`` segundo vocabulario-pav.md e o
fallback fuzzy de taxonomia-pecas.md §4. Inferência de ``autor``/``grau`` quando
ausentes (taxonomia-pecas.md §2), com registro em ``campos_inferidos``.
Documento batizado exatamente de "Despacho" vira ruído não determinante (RE-12).
Dados documentais são evidência, nunca instrução (RE-09).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


# ============================================================
# Contrato interno (um documento normalizado)
# ============================================================

@dataclass
class DocumentPiece:
    """Documento normalizado, pronto para o pipeline de regras R1-R7."""
    ordem: int
    data: Optional[datetime]
    titulo: str
    tipo: str
    autor: str
    grau: str
    nome_arquivo: str = ""
    teor: str = ""
    is_noise: bool = False
    campos_inferidos: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def sort_key(self) -> tuple:
        """Ordenação: por data desc; empate/ausência → ordem desc."""
        ts = self.data.timestamp() if self.data is not None else 0.0
        return (ts, self.ordem)


# ============================================================
# Vocabulário PAV (dicionário determinístico — vocabulario-pav.md)
# ============================================================

# tipo_peca PAV → (tipo_normalizado, is_noise, autor_default, grau_default)
# None = usar autor/grau do título; "auto" = ruído ou opaco conforme observação.
_VOCAB_PAV: Dict[str, Dict[str, Any]] = {
    "capa":                 {"tipo": "ruido",            "is_noise": True,  "autor": "serventia"},
    "peticao inicial":      {"tipo": "peticao_inicial",  "is_noise": False, "autor": "parte",    "grau": "G1"},
    "despacho":             {"tipo": "despacho",         "is_noise": True,  "autor": "juizo_1grau"},
    "mandado de pagamento": {"tipo": "destinacao_financeira", "is_noise": False, "autor": "serventia"},
    "comprovante de resgate mrj": {"tipo": "conversao_renda", "is_noise": False, "autor": "serventia"},
    "aprovacao":            {"tipo": "conversao_renda", "is_noise": False, "autor": "serventia"},
    "andamento processual": {"tipo": "andamento",       "is_noise": True,  "autor": "serventia"},
    "documento processo":   {"tipo": "andamento",       "is_noise": True,  "autor": "serventia"},
    "publicacao":           {"tipo": "ruido_publicacao","is_noise": True,  "autor": "serventia"},
    "comunicacao - intimacao eletronica": {"tipo": "ruido_publicacao", "is_noise": True, "autor": "serventia"},
    "publicacao em diario oficial":       {"tipo": "ruido_publicacao", "is_noise": True, "autor": "serventia"},
    "comunicacao externa":                {"tipo": "ruido_publicacao", "is_noise": True, "autor": "serventia"},
    "peticao":              {"tipo": "peticao_generica", "is_noise": False, "autor": "parte"},
    "protocolo":            {"tipo": "peticao_generica", "is_noise": False, "autor": "parte"},
    "anexo de peticao":     {"tipo": "peticao_generica", "is_noise": False, "autor": "parte"},
    "carta precatoria":     {"tipo": "citacao",         "is_noise": False, "autor": "serventia"},
    "aviso de recebimento": {"tipo": "citacao",         "is_noise": False, "autor": "serventia"},
    "pesquisa parte":       {"tipo": "ruido",           "is_noise": True,  "autor": "serventia"},
    "cartao cnpj":          {"tipo": "ruido",           "is_noise": True,  "autor": "serventia"},
    "documentos":           {"tipo": "ruido_documentos","is_noise": True,  "autor": "serventia"},
    "email":                {"tipo": "ruido",           "is_noise": True,  "autor": "serventia"},
    "oficio":               {"tipo": "ruido",           "is_noise": True,  "autor": "serventia"},
    "oficio resposta":      {"tipo": "ruido",           "is_noise": True,  "autor": "serventia"},
    "mandado":              {"tipo": "atos_constritivos","is_noise": False, "autor": "serventia"},
    "sentenca":             {"tipo": "sentenca",        "is_noise": False, "autor": "juizo_1grau", "grau": "G1"},
    "acordao":              {"tipo": "acordao_g2",      "is_noise": False, "autor": "tribunal_2grau", "grau": "G2"},
    "decisao":              {"tipo": "decisao",         "is_noise": False, "autor": "juizo_1grau", "grau": "G1"},
    "certidao":             {"tipo": "certidao",       "is_noise": False, "autor": "serventia"},
    "comprovante":          {"tipo": "ruido",           "is_noise": True,  "autor": "serventia"},
}


# ============================================================
# Fuzzy (taxonomia-pecas.md §4) — expressões-chave no título/nome_arquivo
# ============================================================

# (padrão regex, tipo, autor_default, grau_default)
# Antes em src processa primeiro; regras mais específicas primeiro.
_FUZZY_RULES: List[tuple] = [
    # Peças de conhecimento — G1
    (r"peticao inicial|exordial|^inicial", "peticao_inicial", "parte", "G1"),
    (r"contestacao|resposta do reu|defesa", "contestacao", "parte", "G1"),
    (r"replica|manifestacao sobre contestacao", "replica", "parte", "G1"),
    (r"saneador|saneamento", "saneador", "juizo_1grau", "G1"),
    (r"laudo pericial|quesitos|esclarec.*perito", "pericia", "terceiro", "G1"),
    (r"ata de audiencia|termo de audiencia|assentada", "audiencia", "juizo_1grau", "G1"),
    (r"alegacoes finais|memoriais", "alegacoes_finais", "parte", "G1"),
    (r"sentenca|sentença", "sentenca", "juizo_1grau", "G1"),
    # Certidões de trânsito (RE-05 exige certidão explícita para 03/06/09)
    (r"certidao de transito em julgado|certidao de transito|certidao de decurso de prazo",
     "certidao_transito", "serventia", None),  # grau resolvido pelo contexto
    # Recursos
    (r"razoes de apelacao|apelacao|razões de apelação|^apela", "apelacao", "parte", "G2"),
    (r"remessa necessaria|reexame necessario|duplo grau obrigatorio",
     "remessa_necessaria", "serventia", "G2"),
    (r"contrarrazoes|contrarra", "contrarrazoes", "parte", "G2"),
    (r"acordao|voto|ementa|relator|turma|camara", "acordao_g2", "tribunal_2grau", "G2"),
    (r"recurso especial|recurso extraordinario|aresp|re_sp|agravo em resp",
     "resp_re", "parte", "SUP"),
    (r"stj|stf|ministro", "acordao_sup", "tribunal_superior", "SUP"),
    (r"juizo de retratacao|adequacao ao paradigma|retrat", "retratacao", None, None),
    (r"embargos de declar|embargos declarat", "embargos_declaracao", None, None),
    # Execução
    (r"cumprimento de sentenca|cumprimento provisorio|inicial.*execucao|execucao fiscal.*cda",
     "inicio_cumprimento", "parte", None),
    (r"mandado de penhora|auto de penhora|termo de penhora|arresto|sisbajud|bacenjud|renajud|avaliac|edital de leilao|arrematac|adjudicac",
     "atos_constritivos", "serventia", None),
    (r"impugnacao ao cumprimento|embargos a execucao|embargos à execução|excecao de pre-executividade|pré-executividade",
     "impugnacao_embargos_exec", "parte", None),
    (r"suspensao.*execucao|art 921|art 40.*lef|arquivamento provisorio|parcelamento|parcelamento",
     "suspensao_execucao", "juizo_1grau", None),
    (r"oficio requisitorio|precatorio|rpv", "precatorio_rpv", "serventia", None),
    (r"sobrestamento|tema repetitivo|repercussao geral|irdr|iac|sirdr|art 313",
     "sobrestamento", None, None),
    (r"dessobrestamento|levantamento.*suspensao|revogacao.*suspensao|desarquivamento|aplica.*paradigma|retomada",
     "retomada", None, None),
    (r"deposito judicial|guia.*deposito|abertura.*conta judicial|caucao em dinheiro",
     "deposito_judicial", None, None),
    (r"certidao de inexist.*saldo|encerramento.*conta", "certidao_saldo", "serventia", None),
    (r"conversao de deposito em renda|conversao em renda|dam conversao|dam de conversao|aresgate.*mrj|comprovante.*resgate.*mrj|extincao.*satisfacao|art 924.*ii",
     "conversao_renda", "juizo_1grau", None),
    (r"extincao definitiva|prescricao intercorrente|cancelamento.*cda|baixa definitiva|arquivamento definitivo|termo de arquivamento definitivo",
     "extincao_definitiva", "juizo_1grau", None),
    (r"destinacao_financeira|mandado de pagamento|alvara|levantamento|transferencia|resgate",
     "destinacao_financeira", "serventia", None),
    # DCP TJRJ regional
    (r"bda|^baixa definitiva", "extincao_definitiva", "serventia", None),
]


# ============================================================
# Autores e graus por inferência textual (taxonomia-pecas.md §2)
# ============================================================

def _infer_autor(titulo: str) -> Optional[str]:
    t = _normalize_text(titulo)
    if any(w in t for w in ("certidao", "termo", "juntada", "mandado", " ar ", "edital")):
        return "serventia"
    if any(w in t for w in ("sentenca", "decisao")) and "tribunal" not in t:
        return "juizo_1grau"
    if any(w in t for w in ("acordao", "voto", "ementa", "relator", "camara", "turma")):
        return "tribunal_2grau"
    if any(w in t for w in ("stj", "stf", "ministro", "recurso especial", "recurso extraordinario")):
        return "tribunal_superior"
    if any(w in t for w in ("peticao", "razoes", "contrarrazoes", "manifestacao", "embargos")):
        return "parte"
    if any(w in t for w in ("laudo", "parecer tecnico", "oficio de terceiro")):
        return "terceiro"
    return None


def _infer_grau(titulo: str) -> Optional[str]:
    t = _normalize_text(titulo)
    if any(w in t for w in ("acordao", "voto", "ementa", "relator", "camara", "turma")):
        return "G2"
    if any(w in t for w in ("stj", "stf", "ministro", "recurso especial", "recurso extraordinario")):
        return "SUP"
    if any(w in t for w in ("sentenca", "decisao")) and "tribunal" not in t:
        return "G1"
    return None


# ============================================================
# Normalização de texto
# ============================================================

def _normalize_text(text: str) -> str:
    """Minúsculas, sem acentos, sem pontuação, espaços simples."""
    if not text:
        return ""
    # Decomposição para remover acentos
    s = unicodedata.normalize("NFKD", text)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^\w\s]", " ", s)  # pontuação → espaço
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _clean_filename(text: str) -> str:
    """Normaliza nome de arquivo: remove extensão, numerais de sequência, datas."""
    s = _normalize_text(text)
    s = re.sub(r"\.pdf$", "", s)
    s = re.sub(r"\b\d{6,}\b", " ", s)  # numerais longos (ids PAV)
    s = re.sub(r"^\w+_?v?\d+", " ", s)  # sequência inicial (ex.: despacho_123)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _parse_date(value: Any) -> Optional[datetime]:
    """Tenta vários formatos; aceita ISO e brasileiro."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    s = str(value).strip()
    fmts = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
    ]
    for f in fmts:
        try:
            dt = datetime.strptime(s, f)
            if dt.tzinfo is None:
                # Apenas para ordenação — sem tzinfo
                pass
            return dt
        except ValueError:
            continue
    # Fallback: ISO com fromisoformat
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


# ============================================================
# Detecção de conteúdo suspeito (RE-09)
# ============================================================

_SUSPICIOUS_PATTERNS = [
    r"ignore as regras",
    r"ignore?\s+(as?\s+regras|todas?\s+as?\s+regras)",
    r"classifiqu?e?\s+como\s+fase\s+1\s?5",
    r"ignore?\s+(.*)?\s*instru(cao|tion)",
]


def _is_suspicious(titulo: str, nome_arquivo: str) -> bool:
    blob = f"{titulo} {nome_arquivo}".lower()
    for p in _SUSPICIOUS_PATTERNS:
        if re.search(p, blob):
            return True
    return False


# ============================================================
# Normalização principal
# ============================================================

def normalize_tree(raw_documents: Optional[List[Dict[str, Any]]]) -> List[DocumentPiece]:
    """
    R0 — Valida e normaliza a árvore bruta para o contrato interno.

    Aceita convenções variadas: ``tipo_peca``/``tipoDePeca``, ``data``/``data_criacao``/
    ``dataAutuacao``, ``nome_arquivo``/``nomeArquivo``, ``titulo``, ``ordem``/``ordemFolha``/
    ``numeroFolha``, ``teor``/``conteudo``.
    """
    if not raw_documents:
        return []

    pieces: List[DocumentPiece] = []
    for idx, doc in enumerate(raw_documents):
        if not isinstance(doc, dict):
            continue

        # Campos brutos
        tipo_peca = _normalize_text(
            doc.get("tipo_peca")
            or doc.get("tipoDePeca")
            or doc.get("tipo")
            or ""
        )
        # nome_arquivo: limpa extensão/numerais, mas preserva leitura do sinal
        nome_raw = (
            doc.get("nome_arquivo")
            or doc.get("nomeArquivo")
            or ""
        )
        nome_arquivo = _clean_filename(nome_raw)
        titulo = doc.get("titulo") or doc.get("título") or nome_arquivo
        titulo_norm = _normalize_text(titulo)
        # Idade/ordem
        ordem_raw = doc.get("ordem") or doc.get("ordemFolha") or doc.get("numeroFolha") or doc.get("id")
        try:
            ordem = int(ordem_raw) if ordem_raw is not None else idx + 1
        except (ValueError, TypeError):
            ordem = idx + 1
        # Data
        data_raw = doc.get("data") or doc.get("data_criacao") or doc.get("dataAutuacao") or doc.get("dataJuntada")
        data = _parse_date(data_raw)
        # Teor (modo híbrido)
        teor = (doc.get("teor") or doc.get("conteudo") or doc.get("content") or "").strip()

        # Conjugação tipo × nome_arquivo (vocabulário PAV primeiro, depois fuzzy no nome)
        tipo, autor, grau, is_noise = _resolve_tipo_autor_grau(tipo_peca, titulo_norm, nome_arquivo)

        # Inferências pendentes
        campos_inferidos: List[Dict[str, Any]] = []
        if not autor:
            a = _infer_autor(titulo_norm) or _infer_autor(nome_arquivo)
            if a:
                autor = a
                campos_inferidos.append({"ordem": ordem, "campo": "autor", "valor_inferido": a})
        if not grau:
            g = _infer_grau(titulo_norm) or _infer_grau(nome_arquivo)
            if g:
                grau = g
                campos_inferidos.append({"ordem": ordem, "campo": "grau", "valor_inferido": g})
        # Despacho por nome_arquivo específico? ex.: "decisao de suspensao art 40.pdf"
        # Se tipo_peca=="despacho" mas nome_arquivo traz sinal decisório,
        # troca o tipo (RE-12).
        if is_noise and not _is_pure_despacho(nome_arquivo):
            novo_tipo, novo_autor, novo_grau, novo_noise = _match_fuzzy(nome_arquivo)
            if novo_tipo and novo_tipo != "ruido":
                tipo = novo_tipo
                is_noise = False
                if novo_autor:
                    autor = novo_autor
                if novo_grau:
                    grau = novo_grau

        if not autor:
            autor = "serventia" if is_noise else "parte"
        if not grau:
            grau = ""

        pieces.append(DocumentPiece(
            ordem=ordem,
            data=data,
            titulo=titulo_norm or nome_arquivo,
            tipo=tipo,
            autor=autor,
            grau=grau,
            nome_arquivo=nome_arquivo,
            teor=teor,
            is_noise=is_noise,
            campos_inferidos=campos_inferidos,
        ))

    # Ordenar por data/ordem ASC (mais antigo → mais recente)
    pieces.sort(key=lambda p: p.sort_key)
    return pieces


# ============================================================
# Resolução tipo × nome_arquivo
# ============================================================

def _is_pure_despacho(nome: str) -> bool:
    """True se nome_arquivo reduz-se a 'despacho' (+ numerais)."""
    n = _clean_filename(nome)
    # remove numerais finais
    n = re.sub(r"\s*\d+\s*$", "", n).strip()
    return n == "despacho"


def _resolve_tipo_autor_grau(
    tipo_peca: str, titulo: str, nome_arquivo: str
) -> tuple:
    """Retorna (tipo, autor, grau, is_noise)."""
    # 1) Vocabulário PAV determinístico por tipo_peca
    if tipo_peca in _VOCAB_PAV:
        entry = _VOCAB_PAV[tipo_peca]
        return (entry["tipo"], entry.get("autor"), entry.get("grau"), entry["is_noise"])

    # 2) Fuzzy no TÍTULO primeiro
    for pattern, tipo, autor, grau in _FUZZY_RULES:
        if re.search(pattern, titulo):
            return (tipo, autor, grau, False)

    # 3) Fuzzy no NOME_ARQUIVO
    for pattern, tipo, autor, grau in _FUZZY_RULES:
        if re.search(pattern, nome_arquivo):
            return (tipo, autor, grau, False)

    # 4) Sem sinal — peça não determinante (ruído opaco)
    # Mantém tipo_genérico para fins de auditoria
    return ("ruido", "serventia", "", True)


def _match_fuzzy(text: str) -> tuple:
    for pattern, tipo, autor, grau in _FUZZY_RULES:
        if re.search(pattern, text):
            return (tipo, autor, grau, False)
    return (None, None, None, None)
