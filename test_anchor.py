import re
import unicodedata

def normalize(texto):
    if not texto:
        return ''
    nfkd = unicodedata.normalize('NFKD', texto)
    ascii_text = nfkd.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'\s+', ' ', ascii_text.lower().strip())

movements = [
    'Definitivo',
    'Baixa Definitiva',
    'Arquivamento',
    'Mero expediente',
    'Expedida/certificada',
    'Decisao',
    'Sentenca'
]

anchor = re.compile(r'\barquivamento\b')

for m in movements:
    norm = normalize(m)
    match = anchor.search(norm)
    print(f'{m:30} -> {norm:30} -> {"MATCH" if match else "no match"}')
