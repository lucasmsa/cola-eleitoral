#!/bin/zsh
# usage: getyt.sh id [id...]  -> raw/yt/<id>.pt-orig.vtt + <id>.info.json (original pt ASR track only)
cd "$(dirname $0)/raw/yt"
for v in "$@"; do
  [ -f "$v.pt-orig.vtt" ] && continue
  ../../../.venv/bin/yt-dlp --no-update --skip-download --write-auto-subs --sub-langs pt-orig --sub-format vtt \
    --write-info-json --extractor-args "youtube:lang=pt" --sleep-requests 2 -o "%(id)s" "https://www.youtube.com/watch?v=$v" > "log_$v.txt" 2>&1
  ls "$v".* 2>/dev/null | tr '\n' ' '; echo
  sleep 8
done
