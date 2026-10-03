import json, re, sys
sys.path.insert(0, 'platform'); from vtt import ts_at
KW = {
 'eco-reforma-tributaria': [r'reforma tribut', r'\bIBS\b', r'\bCBS\b', r'\bIVA\b'],
 'eco-arcabouco': [r'arcabou', r'teto de gasto', r'regra fiscal', r'âncora fiscal', r'gasto público', r'déficit'],
 'eco-privatizacao': [r'privatiz', r'desestatiz', r'estata', r'Petrobras', r'Correios'],
 'eco-bc-autonomo': [r'Banco Central', r'autonomia do banco'],
 'eco-ir-alta-renda': [r'imposto de renda', r'isenç', r'super.?rico', r'altas rendas', r'dividendo', r'5 mil', r'cinco mil'],
 'seg-saidinha': [r'saidinha', r'saída temporária'],
 'seg-drogas': [r'droga', r'maconha', r'descriminaliz', r'usuário'],
 'seg-8-janeiro': [r'8 de janeiro', r'oito de janeiro', r'anistia', r'dosimetria'],
 'seg-armas': [r'\barmas?\b', r'armament', r'desarmament', r'\bCACs?\b'],
 'soc-marco-temporal': [r'marco temporal', r'demarca', r'indígena'],
 'soc-aborto': [r'aborto', r'abortar', r'gestação', r'nascituro'],
 'soc-cotas': [r'\bcotas?\b', r'ação afirmativa', r'ações afirmativas'],
 'amb-licenciamento': [r'licenciamento', r'licença ambiental', r'Ibama'],
 'amb-margem-equatorial': [r'margem equatorial', r'foz do amazonas', r'petróleo'],
 'amb-agrotoxicos': [r'agrot', r'defensivo', r'veneno'],
 'seg-maioridade': [r'maioridade', r'menor de idade', r'16 anos', r'menores infratores', r'imputab'],
 'eco-6x1': [r'6x1', r'6 por 1', r'seis por um', r'escala', r'jornada'],
 'seg-stf-mandato': [r'vitalic', r'mandato (fixo|para)', r'ministros do (STF|supremo)', r'Supremo'],
}
import os
def path(v):
    for d in ('pres2/raw/yt','pres/raw/yt'):
        if os.path.exists(f'{d}/{v}.txt'): return f'{d}/{v}.txt'
    raise SystemExit(f'no captions for {v}')
q, vids = sys.argv[1], sys.argv[2:]
W = int(os.environ.get('W', 300))
for v in vids:
    t = open(path(v)).read(); idx = json.load(open(path(v)+'.idx.json'))
    hits = sorted({m.start() for k in KW[q] for m in re.finditer(k, t, re.I)})
    last = -10**9
    print(f'### {v} hits={len(hits)}')
    for h in hits:
        if h - last < W: continue
        last = h
        print(f'  [{ts_at(idx, h)}] ...{t[max(0,h-W):h+W]}...\n')
