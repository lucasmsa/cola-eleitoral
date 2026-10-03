"""Search YouTube and fetch original pt captions into pres2/raw/yt.
usage: yt.py search "<query>" [n]   |   yt.py get <video_id> [...]"""
import json, os, subprocess, sys, time
sys.path.insert(0, 'platform'); from vtt import flat
D = 'pres2/raw/yt'; YT = '.venv/bin/yt-dlp'; META = f'{D}/meta.txt'


def search(q, n=8):
    out = subprocess.run([YT, '--no-update', '--flat-playlist', '--print', '%(id)s|%(duration)s|%(channel)s|%(title)s', f'ytsearch{n}:{q}'],
                         capture_output=True, text=True, timeout=120)
    print(out.stdout.strip() or out.stderr[-400:])


def get(vid):
    if os.path.exists(f'{D}/{vid}.txt') or os.path.exists(f'pres/raw/yt/{vid}.txt'):
        print(vid, 'cached'); return
    m = subprocess.run([YT, '--no-update', '--no-simulate', '--skip-download', '--print', '%(id)s|%(upload_date)s|%(channel)s|%(title)s',
                        '--write-auto-subs', '--write-subs', '--sub-langs', 'pt-orig,pt-BR', '--sub-format', 'vtt',
                        '--sleep-requests', '2', '-o', f'{D}/%(id)s.%(ext)s', f'https://www.youtube.com/watch?v={vid}'],
                       capture_output=True, text=True, timeout=300)
    line = m.stdout.strip().splitlines()[-1] if m.stdout.strip() else ''
    vtts = [f for f in os.listdir(D) if f.startswith(vid + '.') and f.endswith('.vtt')]
    # original track only: pt-orig auto captions, or manual pt/pt-BR uploaded by the channel
    pick = next((f for f in vtts if '.pt-orig.' in f), None) or next((f for f in vtts if f.endswith('.pt-BR.vtt') or f.endswith('.pt.vtt')), None)
    if not pick or not line:
        print(vid, 'NO CAPTIONS', m.stderr[-300:]); return
    t, idx = flat(f'{D}/{pick}')
    open(f'{D}/{vid}.txt', 'w').write(t); json.dump(idx, open(f'{D}/{vid}.txt.idx.json', 'w'))
    open(META, 'a').write(line + f'|{pick}\n')
    print(vid, len(t), line)


if __name__ == '__main__':
    os.makedirs(D, exist_ok=True)
    if sys.argv[1] == 'search':
        search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8)
    else:
        for v in sys.argv[2:]:
            get(v); time.sleep(3)
