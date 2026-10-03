"""python3 locate.py <video> <quote>: print timestamp, seconds and the 1500 chars before the quote."""
import sys
from caps import META, hms, norm, stream, ts_at
v, q = sys.argv[1], norm(sys.argv[2])
text, starts = stream(v)
i = text.find(q)
print(META.get(v), "found" if i >= 0 else "NOT FOUND")
if i >= 0:
    t = ts_at(starts, i)
    print("ts", hms(t), t, "| count", text.count(q))
    print("BEFORE:", text[max(0, i - 900): i])
