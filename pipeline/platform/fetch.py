import sys, re, html, subprocess, json, os
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/128 Safari/537.36"
def get(url):
    return subprocess.run(['curl','-sL','--max-time','30','-A',UA,url],capture_output=True).stdout.decode('utf-8','ignore')
def text(h):
    h = re.sub(r'(?is)<(script|style|noscript|svg).*?</\1>', ' ', h)
    h = re.sub(r'(?s)<[^>]+>', ' ', h)
    return re.sub(r'\s+', ' ', html.unescape(h)).strip()
def slug(url): return re.sub(r'[^a-z0-9]+','-', url.split('//',1)[1].lower())[:150]
if __name__ == '__main__':
    for u in sys.argv[1:]:
        h = get(u); t = text(h)
        m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', h)
        p = f'platform/raw/{slug(u)}.txt'
        open(p,'w').write(t)
        print(len(t), (m.group(1) if m else '?'), p)
