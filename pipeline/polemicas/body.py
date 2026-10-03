import sys, re
from fetch import fetch, text_of
url, start = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 2500
t = text_of(fetch(url))
i = t.find(start)
print(t[i:i + n] if i >= 0 else "START NOT FOUND; len=%d; head=%s" % (len(t), t[:600]))
