// Film renderer, after claude-motion-design's render_template.py, ported to Node Playwright.
//   node render.mjs probe <w> <h> t1 t2 ...        -> out/probe-<w>x<h>.png (4-column sheet)
//   node render.mjs still <w> <h> <t> <file>       -> one PNG at t (supersampled 2x, Lanczos down)
//   node render.mjs full <w> <h> <out.mp4> [loop]  -> 60 fps, SUB subframes on a 180 degree shutter, tmix blend
//   node render.mjs pops <video>                   -> single-frame pops and one-frame flashes
// Serve the repo root first: python3 -m http.server 8791 --directory <repo>
import { chromium } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import { mkdirSync, rmSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, 'out');
const BASE = 'http://localhost:8791/design/film/film.html';
const FPS = 60, SUB = 6, SHUTTER = 0.5;
const ARGS = ['--deterministic-mode', '--run-all-compositor-stages-before-draw', '--disable-threaded-animation',
  '--disable-checker-imaging', '--font-render-hinting=none', '--force-color-profile=srgb'];

async function open(w, h, { loop = false, scale = 1 } = {}) {
  const browser = await chromium.launch({ args: ARGS, executablePath: process.env.PW_CHROMIUM });
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
  const errs = [];
  page.on('pageerror', (e) => errs.push(String(e)));
  page.on('console', (m) => { if (['error', 'warning'].includes(m.type())) errs.push('console: ' + m.text()); });
  await page.goto(`${BASE}?w=${w}&h=${h}${loop ? '&loop=1' : ''}`);
  await page.waitForFunction('window.ready === true', null, { timeout: 300000 });
  await page.evaluate('document.fonts.ready');
  await page.addStyleTag({ content: '*,*::before,*::after{transition:none!important;animation:none!important}' });
  const T = await page.evaluate('window.DURATION');
  return { browser, page, errs, T };
}

async function shot(page, t, path, type = 'png') {
  await page.evaluate(`window.seek(${t})`);
  await page.evaluate('new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))');
  const el = await page.$('#stage');
  await el.screenshot({ path, type, ...(type === 'jpeg' ? { quality: 95 } : {}) });
}

function ff(args) { execFileSync('ffmpeg', ['-v', 'error', '-y', ...args], { stdio: 'inherit' }); }

async function probe(w, h, times) {
  const dir = join(OUT, `probe-${w}x${h}`); rmSync(dir, { recursive: true, force: true }); mkdirSync(dir, { recursive: true });
  const { browser, page, errs } = await open(w, h);
  for (const [i, t] of times.entries()) await shot(page, t, join(dir, `p_${String(i).padStart(2, '0')}.png`));
  await browser.close();
  if (errs.length) console.log('PAGE ERRORS:', errs.slice(0, 8));
  const rows = Math.ceil(times.length / 4);
  ff(['-i', join(dir, 'p_%02d.png'), '-vf', `scale=480:-1,tile=4x${rows}:padding=8:color=white`, '-frames:v', '1', join(OUT, `probe-${w}x${h}.png`)]);
  console.log('probe ->', join(OUT, `probe-${w}x${h}.png`));
}

async function still(w, h, t, file) {
  const { browser, page, errs } = await open(w, h, { scale: 2 });
  const tmp = join(OUT, `still-${w}x${h}@2x.png`);
  await shot(page, t, tmp);
  await browser.close();
  if (errs.length) console.log('PAGE ERRORS:', errs.slice(0, 8));
  ff(['-i', tmp, '-vf', `scale=${w}:${h}:flags=lanczos`, file]);
  console.log('still ->', file);
}

async function full(w, h, file, loop) {
  const sub = join(OUT, `sub-${w}x${h}${loop ? '-loop' : ''}`); rmSync(sub, { recursive: true, force: true }); mkdirSync(sub, { recursive: true });
  const { browser, page, errs, T } = await open(w, h, { loop });
  const n = Math.round(T * FPS);
  const offs = [...Array(SUB).keys()].map((j) => (j - (SUB - 1) / 2) * SHUTTER / (FPS * SUB));
  let k = 0;
  for (let i = 0; i < n; i++) {
    for (const o of offs) {
      // subframes of the first frame never reach back before 0; a loop wraps instead
      let t = i / FPS + o;
      t = loop ? (t + T) % T : Math.min(T - 1e-3, Math.max(0, t));
      await shot(page, t, join(sub, `s_${String(k).padStart(6, '0')}.jpg`), 'jpeg'); k++;
    }
    if (i % 60 === 0) console.log(`${w}x${h} frame ${i}/${n}`);
  }
  await browser.close();
  if (errs.length) console.log('PAGE ERRORS:', errs.slice(0, 8));
  const vf = `tmix=frames=${SUB},select='eq(mod(n\\,${SUB})\\,${SUB - 1})',setpts=N/${FPS}/TB,` +
    'scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p';
  ff(['-framerate', String(FPS * SUB), '-i', join(sub, 's_%06d.jpg'), '-vf', vf, '-r', String(FPS),
    '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', '-color_range', 'tv', '-colorspace', 'bt709',
    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-movflags', '+faststart', file]);
  console.log('video ->', file);
}

function pops(video) {
  const S = 180;
  const raw = execFileSync('ffmpeg', ['-v', 'quiet', '-i', video, '-vf', `scale=${S}:${S},format=gray`, '-f', 'rawvideo', '-'], { maxBuffer: 1 << 30 });
  const n = raw.length / (S * S);
  const frame = (i) => raw.subarray(i * S * S, (i + 1) * S * S);
  const diff = (a, b) => { let s = 0; for (let j = 0; j < a.length; j++) s += Math.abs(a[j] - b[j]); return s / a.length; };
  const d = []; for (let i = 0; i < n - 1; i++) d.push(diff(frame(i), frame(i + 1)));
  const hits = [], flashes = [];
  for (let i = 1; i < d.length - 1; i++) {
    const nb = Math.max(d[i - 1], d[i + 1], 0.3);
    if (d[i] > 3 * nb && d[i] > 2) hits.push([i + 1, ((i + 1) / FPS).toFixed(3), d[i].toFixed(2)]);
  }
  for (let i = 1; i < n - 1; i++) {
    const a = d[i - 1], b = d[i], skip = diff(frame(i - 1), frame(i + 1));
    if (Math.min(a, b) > 2 && skip < 0.35 * Math.min(a, b)) flashes.push([i, (i / FPS).toFixed(3)]);
  }
  console.log(`frames ${n}, pops ${hits.length}`, hits.slice(0, 12), `flashes ${flashes.length}`, flashes.slice(0, 12));
}

const [cmd, ...a] = process.argv.slice(2);
mkdirSync(OUT, { recursive: true });
if (cmd === 'probe') await probe(+a[0], +a[1], a.slice(2).map(Number));
else if (cmd === 'still') await still(+a[0], +a[1], +a[2], a[3]);
else if (cmd === 'full') await full(+a[0], +a[1], a[2], a[3] === 'loop');
else if (cmd === 'pops') pops(a[0]);
else console.log('usage: probe|still|full|pops');
if (!existsSync(OUT)) mkdirSync(OUT);
