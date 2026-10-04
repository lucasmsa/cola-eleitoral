# Cover film

Built with the method of [howseen-ai/claude-motion-design](https://github.com/howseen-ai/claude-motion-design) (read from a scratch clone, not installed as a skill): one HTML page whose every frame comes from `window.seek(t)`, captured by Playwright, blended for motion blur, encoded with ffmpeg.

- `film.html?w=&h=[&loop=1]`: the film. No CSS transitions or timers. The Rive files (`public/mascot/calango.riv`, `public/rive/carimbo.riv`, `public/rive/pagina.riv`) run on the low-level runtime and are stepped by `seek(t)` in fixed slices of at most 1/120 s, so a frame depends only on `t`. Space, arrows and `r` preview it in a browser.
- `render.mjs`: `probe`, `still`, `full`, `pops`. Full renders take 6 subframes per frame over a 180 degree shutter, blend them with `tmix`, and encode H.264 at crf 16 in TV-range BT.709. Deterministic Chromium flags as in the method's section 9c.

```
python3 -m http.server 8791 --directory .        # repo root
export PW_CHROMIUM=<chromium headless shell>      # optional
node design/film/render.mjs probe 1600 900 1 3 5 7 9
node design/film/render.mjs full 1600 900 design/film/out/cover-1600x900.mp4
node design/film/render.mjs full 1080 1080 design/film/out/cover-1080x1080.mp4
node design/film/render.mjs full 1600 900 design/film/out/cover-loop-1600x900.mp4 loop
node design/film/render.mjs still 1600 900 8.983333333333333 public/cover.png
node design/film/render.mjs still 1200 630 8.983333333333333 public/og.png
ffmpeg -i design/film/out/cover-1600x900.mp4 -vf scale=1280:720:flags=lanczos -c:v libvpx-vp9 -b:v 0 -crf 34 -row-mt 1 -an public/cover-loop.webm
```

Timeline (9 s, 60 fps): ruled lines draw in (0 to 1.0 s); the Calango walks on from the left (0.55 to 3.0 s) and nods on arrival; it watches "Cola Eleitoral" being written letter by letter in Kalam with a pen nib (3.35 s on), then the pen-orange underline, its pupils and head following the nib line by line; its eyes then follow the subtitle as it rises word by word (5.75 s); when the REGISTRADO stamp thumps at 6.6 s (small camera punch) it nods and glances up at the stamp, then returns to the viewer by about 8 s; the last second holds the cover frame with the idle breathing and tail sway still running. The gaze is pure in t: the target (nib, current word, stamp) is averaged over a 0.12 s trailing window and drives the `Pupil 0`, `Pupil 1`, `Head` and `Head rim` nodes after each Rive step, so `calango.riv` itself is unchanged. `public/cover.png` and `og.png` are stills at t = 539/60 s, the last video frame, so the app can hold the poster after the video ends. The webm (`public/cover-loop.webm`, kept name) is the 1600x900 cut scaled to 1280x720 and plays once.

Rendering three cuts in parallel on a loaded machine made two of them stall at page load; render them one at a time.

No audio.
