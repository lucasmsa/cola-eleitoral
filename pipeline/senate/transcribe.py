"""Local ASR (faster-whisper) of cached YouTube audio into WebVTT, used when YouTube captions are rate-limited."""
import glob
import os
import sys
from faster_whisper import WhisperModel

HERE = os.path.dirname(os.path.abspath(__file__))
YT = os.path.join(HERE, 'raw', 'yt')
MODEL = sys.argv[1] if len(sys.argv) > 1 else 'small'


def ts(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f'{int(h):02d}:{int(m):02d}:{s:06.3f}'


model = WhisperModel(MODEL, device='cpu', compute_type='int8', cpu_threads=8)
for audio in sorted(p for ext in ('m4a', 'webm', 'opus') for p in glob.glob(os.path.join(YT, f'*.audio.{ext}'))):
    vid = os.path.basename(audio).split('.audio.')[0]
    out = os.path.join(YT, f'{vid}.whisper-{MODEL}.pt.vtt')
    if os.path.exists(out):
        continue
    segments, info = model.transcribe(audio, language='pt', beam_size=5, vad_filter=True)
    with open(out + '.tmp', 'w') as fh:
        fh.write(f'WEBVTT\nNOTE faster-whisper {MODEL}, language pt, transcribed locally from {vid}\n\n')
        for seg in segments:
            fh.write(f'{ts(seg.start)} --> {ts(seg.end)}\n{seg.text.strip()}\n\n')
    os.replace(out + '.tmp', out)
    print('done', vid, flush=True)
