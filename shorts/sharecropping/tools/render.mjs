#!/usr/bin/env node
// Frame-exact render of sharecropping.html to MP4 (1080x1920, 30 fps) with audio/mix.wav, plus QA helpers.
//
//   node tools/render.mjs                      -> out/sharecropping_short.mp4 (then: python3 tools/master.py ...)
//   node tools/render.mjs --stills 0,5,12.5    -> out/stills/*.jpg and out/stills/sheet.jpg (one frame per time)
//   node tools/render.mjs --check              -> dead-zone audit + overlap/safe-zone audit at 0.5 s steps
//
// GSAP is not committed (the page loads 3.13.0 from jsDelivr). For an offline render, point GSAP_DIR at a local
// gsap/dist folder (npm i gsap@3.13.0) and the CDN requests are served from it.
import {createRequire} from 'module';
import {spawn, execFileSync} from 'child_process';
import fs from 'fs';
import path from 'path';
import {fileURLToPath} from 'url';

const require = createRequire(import.meta.url);
const {chromium} = require('playwright');
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const arg = (f, d) => { const i = process.argv.indexOf(f); return i > -1 ? process.argv[i + 1] : d; };
const has = (f) => process.argv.includes(f);
const FPS = 30;
const OUT = path.join(ROOT, 'out');
fs.mkdirSync(OUT, {recursive: true});

const browser = await chromium.launch();
const page = await browser.newPage({viewport: {width: 1080, height: 1920}, deviceScaleFactor: 1});
page.on('pageerror', (e) => { console.error('page error:', e.message); process.exitCode = 1; });
const GSAP_DIR = process.env.GSAP_DIR;
if (GSAP_DIR) {
  await page.route('https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/*', (r) =>
    r.fulfill({path: path.join(GSAP_DIR, path.basename(new URL(r.request().url()).pathname))}));
}
await page.goto('file://' + path.join(ROOT, 'sharecropping.html') + '?render=1');
await page.waitForFunction(() => window.__ready === true, null, {timeout: 30000});
const DUR = await page.evaluate(() => window.__dur);

if (has('--check')) {
  // 1. dead zones: the picture should change every 3-5 s (Shorts checklist); flag any gap over 4 s
  const beats = await page.evaluate(() => window.__beats());
  let prev = 0, gaps = [];
  for (const b of [...beats, DUR - 3]) { if (b - prev > 4) gaps.push(`${prev.toFixed(1)}->${b.toFixed(1)}`); prev = Math.max(prev, b); }
  console.log(`beats: ${beats.length}, gaps over 4 s: ${gaps.join(', ') || 'none'}`);

  // 2. overlap + safe zones, sampled every 0.5 s. Text never touches other text; scene text stays in x 60-930
  //    (60-1020 above y 900), y 150-1150; captions and source tags have their own bands.
  const issues = new Map();
  for (let t = 0; t <= DUR; t += 0.5) {
    const found = await page.evaluate((t) => {
      window.renderAt(t);
      const vis = (el) => { let o = 1; for (let e = el; e && e.id !== 'stage'; e = e.parentElement) { const cs = getComputedStyle(e); if (cs.visibility === 'hidden' || cs.display === 'none') return 0; o *= +cs.opacity; } return o; };
      const els = [...document.querySelectorAll('.tape, .slip, .lab, .hand, .colhead, .defbar, #s0kick, #cap, .tag, .scene .abs:not(.bale):not(#s4bale)')]
        .filter((e) => e.textContent.trim() && vis(e) > 0.05 && !e.closest('#s5months'));
      const name = (e) => '#' + (e.id || (e.closest('[id]').id + '>' + e.className.split(' ')[0] + ':' + e.textContent.trim().slice(0, 14)));
      const R = els.map((e) => ({e, r: e.getBoundingClientRect(), n: name(e)}));
      const out = [];
      for (let i = 0; i < R.length; i++) {
        const {r, n, e} = R[i];
        if (!['cap', ''].includes(e.id) || true) {
          const scene = !e.matches('#cap, .tag');
          if (scene && (r.left < 56 || r.top < 150 || r.bottom > 1152 || r.right > (r.bottom > 900 ? 934 : 1024))) out.push(`${n} outside safe zone [${r.left|0},${r.top|0},${r.right|0},${r.bottom|0}]`);
        }
        for (let j = i + 1; j < R.length; j++) {
          const a = r, b = R[j].r;
          if (R[j].e.contains(e) || e.contains(R[j].e)) continue;
          const ok = e.closest('[data-ovl-ok]') && R[j].e.closest('[data-ovl-ok]');
          const ix = Math.min(a.right, b.right) - Math.max(a.left, b.left), iy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
          if (ix > 4 && iy > 4 && !ok) out.push(`${n} overlaps ${R[j].n}`);
        }
      }
      return out;
    }, t);
    for (const f of found) { if (!issues.has(f)) issues.set(f, []); issues.get(f).push(t.toFixed(1)); }
  }
  if (!issues.size) console.log('overlap/safe-zone audit: clean');
  for (const [f, ts] of issues) console.log(`  ${f}  @ ${ts.length > 6 ? ts[0] + '..' + ts[ts.length - 1] : ts.join(',')}`);
} else if (arg('--stills')) {
  const dir = path.join(OUT, 'stills');
  fs.rmSync(dir, {recursive: true, force: true});
  fs.mkdirSync(dir, {recursive: true});
  const times = arg('--stills').split(',').map(Number);
  for (const [i, t] of times.entries()) {
    await page.evaluate((t) => window.renderAt(t), t);
    await page.screenshot({path: path.join(dir, `${String(i).padStart(2, '0')}_${t.toFixed(2)}.jpg`), type: 'jpeg', quality: 85});
  }
  const cols = Math.min(times.length, 6);
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-pattern_type', 'glob', '-i', path.join(dir, '*.jpg'),
    '-vf', `scale=360:-1,tile=${cols}x${Math.ceil(times.length / cols)}:padding=6:color=0x333333`, '-frames:v', '1', path.join(dir, 'sheet.jpg')]);
  console.log('stills ->', dir);
} else {
  const n = Math.round(DUR * FPS);
  const out = arg('--out', path.join(OUT, 'sharecropping_short.mp4'));
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-i', path.join(ROOT, 'audio', 'mix.wav'), '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], {stdio: ['pipe', 'inherit', 'inherit']});
  const t0 = Date.now();
  for (let f = 0; f < n; f++) {
    await page.evaluate((t) => window.renderAt(t), f / FPS);
    const buf = await page.screenshot({type: 'jpeg', quality: 92});
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(`frame ${f}/${n} (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  console.log('rendered ->', out);
}
await browser.close();
