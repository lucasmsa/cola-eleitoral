import sys
v, s = sys.argv[1], sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
t = open(f'pres/raw/yt/{v}.txt').read(); i = t.find(s)
print(i, t[i:i+n] if i >= 0 else 'NOT FOUND')
