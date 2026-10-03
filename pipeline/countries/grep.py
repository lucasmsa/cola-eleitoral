import re, sys
from fetch import text
url, pat = sys.argv[1], sys.argv[2]
t = text(url)
ms = list(re.finditer(pat, t))
print(f"== {url} len={len(t)} hits={len(ms)}")
for m in ms[:3]:
    print("  ::", t[max(0, m.start() - 150): m.end() + 200])
