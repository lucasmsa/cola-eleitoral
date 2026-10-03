import json, re, glob, sys, unicodedata
def norm(s): return re.sub(r'\s+', ' ', s)
KW = {
 'eco-reforma-tributaria': [r'reforma tribut', r'\bIBS\b', r'\bCBS\b', r'\bIVA\b'],
 'eco-arcabouco': [r'arcabou', r'teto de gastos', r'regra fiscal', r'âncora fiscal', r'equil[ií]brio fiscal', r'd[eé]ficit zero'],
 'eco-privatizacao': [r'privatiz', r'desestatiz', r'Eletrobr', r'estatais'],
 'eco-bc-autonomo': [r'Banco Central'],
 'eco-ir-alta-renda': [r'imposto de renda', r'isenç', r'super.?ricos', r'altas rendas', r'grandes fortunas', r'dividendos', r'5 mil'],
 'seg-saidinha': [r'saidinha', r'saída temporária', r'saidas tempor'],
 'seg-drogas': [r'drogas', r'descriminaliz', r'maconha', r'entorpecente'],
 'seg-8-janeiro': [r'8 de janeiro', r'anistia', r'dosimetria', r'golpis'],
 'seg-blindagem': [r'blindagem', r'imunidade parlamentar', r'prerrogativa'],
 'seg-armas': [r'\barmas?\b', r'armament', r'desarmament', r'\bCACs?\b', r'legítima defesa'],
 'soc-marco-temporal': [r'marco temporal', r'demarcaç', r'terras? ind[ií]gena'],
 'soc-aborto': [r'aborto', r'nascituro', r'desde a concepç', r'interrupção (voluntária|legal) da gravidez', r'direitos reprodutivos'],
 'soc-cotas': [r'\bcotas\b', r'ações afirmativas', r'ação afirmativa'],
 'amb-licenciamento': [r'licenciamento'],
 'amb-margem-equatorial': [r'Margem Equatorial', r'foz do Amazonas', r'petróleo'],
 'amb-agrotoxicos': [r'agrot[oó]xico', r'defensivos', r'pesticida', r'veneno'],
}
mp = json.load(open('platform/plan_map.json'))
q = sys.argv[1]; cands = sys.argv[2:] or None
if q not in KW: KW[q] = [q]
W = int(__import__("os").environ.get("W","220"))
for f, m in mp.items():
    if m['status'] == 'INDEFERIDO': continue
    if cands and m['candidateId'] not in cands: continue
    hits = []
    for p in sorted(glob.glob(f'platform/text/{f}.p*.txt'), key=lambda x: int(x.rsplit('.p',1)[1][:-4])):
        pg = int(p.rsplit('.p',1)[1][:-4]); t = norm(open(p).read())
        for k in KW[q]:
            for mm in re.finditer(k, t, re.I):
                hits.append((pg, t[max(0,mm.start()-W):mm.end()+W]))
    print(f"### {m['candidateId']} {m['name']} hits={len(hits)}")
    seen=set()
    for pg, s in hits[:int(__import__('os').environ.get('N','4'))]:
        if s[:80] in seen: continue
        seen.add(s[:80]); print(f"  p{pg}: {s}")
