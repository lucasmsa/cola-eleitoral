import os
def path(v):
    for d in ('pres2/raw/yt', 'pres/raw/yt'):
        if os.path.exists(f'{d}/{v}.txt'):
            return f'{d}/{v}.txt'
    raise SystemExit(f'no captions for {v}')
