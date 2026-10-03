import sys
from fetch import text
url, *keys = sys.argv[1:]
t = text(url)
print(f"== {url} len={len(t)}")
for k in keys:
    i = t.find(k.lower())
    print(f"  [{k}]", t[max(0, i - 160): i + 260] if i >= 0 else "NOT FOUND")
