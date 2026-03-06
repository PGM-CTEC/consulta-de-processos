import re
import logging
import unicodedata

logger = logging.getLogger(__name__)

_REPLACEMENTS = {
    "C\ufffdMARA": "CÂMARA",
    "C\ufffdVEL": "CÍVEL",
    "C\ufffdVEIS": "CÍVEIS",
    "P\ufffdBLICA": "PÚBLICA",
    "P\ufffdBLICAS": "PÚBLICAS",
    "P\ufffdBLICOS": "PÚBLICOS",
    "FAM\ufffdLIA": "FAMÍLIA",
    "INF\ufffdNCIA": "INFÂNCIA",
    "J\ufffdRI": "JÜRI",
    "\ufffdRF\ufffdOS": "ÓRFÃOS",
    "SUCESS\ufffdES": "SUCESSÕES",
    "EXECU\ufffd\ufffdO": "EXECUÇÃO",
    "EXECU\ufffd\ufffdES": "EXECUÇÕES",
    "JURISDI\ufffd\ufffdO": "JURISDIÇÃO",
    "COM\ufffdRCIO": "COMÉRCIO",
    "TR\ufffdNSITO": "TRÂNSITO",
    "S\ufffdO": "SÃO",
    "JO\ufffdO": "JOÃO",
    "SA\ufffdDE": "SAÚDE",
    "PREVIDENCI\ufffdRIA": "PREVIDENCIÁRIA",
    "PREVIDENCI\ufffdRIO": "PREVIDENCIÁRIO",
    "VIOL\ufffdNCIA": "VIOLÊNCIA",
    "DOM\ufffdSTICA": "DOMÉSTICA",
    "COMPET\ufffdNCIA": "COMPETÊNCIA",
    "F\ufffdRUM": "FÓRUM",
    "TRIBUNAL DE JUSTI\ufffdA": "TRIBUNAL DE JUSTIÇA",
    "JUSTI\ufffdA": "JUSTIÇA",
    "8\ufffd": "8ª",
}

_COMPILED_PATTERNS = [
    (re.compile(re.escape(bad), re.IGNORECASE), good)
    for bad, good in _REPLACEMENTS.items()
]

def remove_accents(text: str) -> str:
    """
    Remove diacritical marks (accents) from a string.
    Converts "Câmara" to "Camara", "São" to "Sao", etc.

    This prevents encoding issues with special characters that the API may return.
    """
    if not text or not isinstance(text, str):
        return text

    # Normalize to NFD (decompose accented characters)
    nfd = unicodedata.normalize('NFD', text)

    # Filter out combining marks (diacriticals)
    return ''.join(
        char for char in nfd
        if unicodedata.category(char) != 'Mn'
    )


def clean_orgao_name(name: str) -> str:
    if not name or not isinstance(name, str):
        return name
        
    # Pre-clean known literals that are hard to catch with encode/decode
    fixed_name = name
    fixed_name = fixed_name.replace("PRESID\u00c3NCIA", "PRESIDÊNCIA")
    fixed_name = fixed_name.replace("PRESID\u00c3\u0160NCIA", "PRESIDÊNCIA")
    fixed_name = fixed_name.replace("PRESIDENCIA", "PRESIDÊNCIA")
    fixed_name = fixed_name.replace("PRIMEIRA CAMARA", "PRIMEIRA CÂMARA")
    
    # Vara numbers
    fixed_name = re.sub(r'(\d)\s+VARA', r'\1ª VARA', fixed_name, flags=re.IGNORECASE)
    fixed_name = re.sub(r'(\d)VARA', r'\1ª VARA', fixed_name, flags=re.IGNORECASE)

    # Pass 2: Try to fix utf-8 incorrectly interpreted as cp1252
    try:
        if "Ã" in fixed_name or "ï¿½" in fixed_name:
            fixed_name = fixed_name.encode('cp1252').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    # Pass 3: Dictionary replacements
    for pattern, good in _COMPILED_PATTERNS:
        def repl_func(match):
            matched_str = match.group(0)
            if matched_str.isupper():
                return good.upper()
            elif matched_str.islower():
                return good.lower()
            elif matched_str.istitle() or (len(matched_str) > 0 and matched_str[0].isupper()):
                return good.title()
            return good

        fixed_name = pattern.sub(repl_func, fixed_name)

    # Pass 4: Final fallback - remove any remaining accents to prevent encoding errors
    # This ensures no character encoding issues reach the frontend
    fixed_name = remove_accents(fixed_name)

    return fixed_name

if __name__ == "__main__":
    t1 = "PRESID\u00c3NCIA"
    print(f"Test 1: {t1} -> {clean_orgao_name(t1)}")
    t2 = "8 VARA"
    print(f"Test 2: {t2} -> {clean_orgao_name(t2)}")
    t3 = "PRIMEIRA CAMARA"
    print(f"Test 3: {t3} -> {clean_orgao_name(t3)}")
