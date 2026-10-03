"""Helpers to read cached captions: python3 captions.py <vtt> <from> <to> | --grep <vtt> <regex>"""
import os
import re
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'checks'))
from check_senate import parse_vtt, to_seconds  # noqa: E402


def fmt(t):
    return f'{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d}'


if __name__ == '__main__':
    if sys.argv[1] == '--grep':
        cues = parse_vtt(sys.argv[2])
        rx = re.compile(sys.argv[3], re.I)
        for i, (t, line) in enumerate(cues):
            if rx.search(line):
                print(fmt(t), ' / '.join(c[1] for c in cues[max(0, i - 1):i + 3])[:400])
    else:
        a, b = to_seconds(sys.argv[2]), to_seconds(sys.argv[3])
        for t, line in parse_vtt(sys.argv[1]):
            if a <= t <= b:
                print(fmt(t), line)
