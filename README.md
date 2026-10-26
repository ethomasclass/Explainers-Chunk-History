> **Imported copy.** Copied from [BusyBee3333/animated-explainer-skills](https://github.com/BusyBee3333/animated-explainer-skills) (commit `c1dd704`, MIT license, see [LICENSE](LICENSE)) as a starting point for short Chunk History explainers. `.claude/skills` links to `skills/` so Claude Code loads the four skills in this repo. The long-form 15-minute style lives separately in `15minhistorystyle` and is unchanged.

# Animated Explainer Skills — build Kurzgesagt-quality explainer videos as self-contained HTML

Everything you need to produce a **Kurzgesagt-style animated explainer video** that plays like a finished YouTube animation — layered parallax worlds, a flying host mascot, physics-feeling choreography, a seekable player — and ships as **one self-contained HTML file**. It's a complete production system: the choreography **patterns**, a **YouTube-retention method**, a **0.5s-resolution overlap auditor**, and a **per-scene ElevenLabs voiceover pipeline** — packaged as [Claude Code](https://claude.com/claude-code) skills **and** as standalone docs + tools you can run without Claude.

[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](LICENSE)
[![GSAP 3.13 — free](https://img.shields.io/badge/GSAP-3.13%20free-88CE02.svg)](https://gsap.com/)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)

---

## New here? Start guided

Copy `skills/` into your project's `.claude/skills/`, then tell Claude Code: **"use explainer-studio and guide me through building an explainer about &lt;topic&gt;"** — it walks you through all 7 phases (script → assets → choreography → retention → gates → voiceover → publish) with an exit checklist at every step.

## What you get

- **Four skills**: `explainer-studio` (**start here** — the guided 7-phase path from blank file to published video), `explainer-assets` (generating crafted components, props, characters & worlds), `gsap-explainer` (choreography + production), `retention-pass` (the YouTube-retention method).
- **A runnable 5-scene reference build** (`skills/gsap-explainer/scaffold.html`) with every pattern in context — the worked example is "How Compound Interest Snowballs", fully swappable.
- **Physics that feels physical** — `CustomBounce` drops with **squash-and-stretch** (the squash *is* the weight), `Physics2D` bursts with replay-identical index-seeded debris.
- **The Kurzgesagt "fuse" move** — `MorphSVG` turns N objects into the concept they represent ("same objects, new shape", literally).
- **A camera rig** — vignette + grain, per-cut parallax dolly across 3 depth layers, push-ins on payoffs, scene-cut wipes.
- **A flying host mascot** that points, taps, hops and reacts — a friendly bee by default (like Kurzgesagt's birds), rebrandable by swapping one SVG string.
- **Population-as-characters** — quantities are little characters, not dots.
- **A seekable player** — click-to-seek bar, chapter ticks, ←/→ keys, autoplay-on-scroll, reduced-motion fallback.
- **A 3-round YouTube-retention method** — hook/peak loop audit, dead-zone killing, VO-sync, freeze-frame verification.
- **A 0.5s-resolution pairwise overlap auditor** — catches "words on words" and host-strikes-headline collisions the frozen preview silently hides.
- **A per-scene ElevenLabs voiceover pipeline** — write at 2.5 words/sec, synth one clip per scene, auto-report which scenes to extend.

## Quickstart

**With Claude Code (recommended):**
1. `git clone` this repo.
2. Copy the skills into your project: `cp -r skills/gsap-explainer skills/retention-pass /path/to/your/project/.claude/skills/`
3. Ask Claude Code: **"build me an explainer video about \<your topic\>"** — it picks up the `gsap-explainer` skill and follows the method.

**Standalone (no Claude):**
1. `git clone` this repo, then `cd skills/gsap-explainer`.
2. `python3 inline-gsap.py scaffold.html` — fetches GSAP 3.13 from the public CDN into a gitignored `vendor/` and inlines it.
3. Open `scaffold.html` in a browser. It plays. Now duplicate it and replace the scenes with your content, using the reference scenes as your idiom source (read `skills/gsap-explainer/SKILL.md` — it's a full standalone manual).

## Tools

**Overlap auditor** — inject into the running page, then sweep every scene for collisions at 0.5s resolution:
```js
// paste skills/gsap-explainer/tools/overlap-audit.js into the console
__ovlAuditAll(0.5)   // -> { S3: [ {a, b, pen, ...} ] }  (empty = clean)
```

**Beat auditor** — map choreography coverage vs scene durations, find dead zones:
```bash
node skills/retention-pass/tools/beat-audit.mjs your-video.html
# prints per scene: last-beat time, coverage %, gaps > 4s
```

**Voiceover pipeline** — generate one ElevenLabs clip per scene + a fit report:
```bash
export ELEVENLABS_API_KEY=...        # or put it in ./.env
python3 skills/gsap-explainer/tools/vo-generate.py your-video-script.md ./vo <voiceId>
# S0: 12.3s / 15s = 82%  OK
# S3: 31.4s / 30s = 105% OVER -> extend scene to 33
```

## The method

The short version: **script → scaffold → choreography → retention pass → VO-sync → zero-overlap gates → VO pipeline.** Write a shot script first (per scene: duration, visual, on-screen text, VO line). Copy the scaffold. Replace scenes one at a time, adapting patterns instead of inventing them. Run the retention pass *before* recording VO (that's when durations are free). Clear the overlap auditor at 0.5s steps. Then generate per-scene voiceover and extend any scene its clip overran.

The full pipeline narrative for humans is in **[docs/METHOD.md](docs/METHOD.md)**. The two skills — [`gsap-explainer`](skills/gsap-explainer/SKILL.md) and [`retention-pass`](skills/retention-pass/SKILL.md) — are the exhaustive references, readable on their own.

## FAQ

**Why HTML instead of After Effects?** It's diffable, scriptable, and version-controllable; it ships as a few hundred KB of vector that plays in any browser; every quantity, label and timing is data you can edit in seconds; and an LLM can author it. You screen-record the playback to get an MP4 for YouTube.

**Is GSAP really free?** Yes — 100% free, including every formerly-premium plugin (DrawSVG, MorphSVG, SplitText, Physics2D, MotionPath, Flip, the Custom* eases, ...), since Webflow's 2025 acquisition of GSAP. This repo ships no GSAP code; `inline-gsap.py` fetches it from the public CDN for you.

**Can I rebrand the mascot?** Yes. The default host is a friendly bee (Kurzgesagt-style). To reskin: change the color tokens in the scaffold's `:root` and replace the `host()` SVG string. The faces API, arm-pointing, and flight rig all keep working.

**Does it work without Claude Code?** Yes. The skills are Markdown; the tools are plain Python/Node; the scaffold is a normal HTML file. Claude Code just automates following the method.

## Contributing

PRs welcome — new choreography patterns, additional host mascots, retention findings, and tooling improvements especially. Keep the scaffold self-contained and the tools dependency-free.

## License

MIT — see [LICENSE](LICENSE).

---

<sub>Keywords: animated explainer video · GSAP animation · Kurzgesagt style · Claude Code skills · motion design · YouTube retention · educational video · SVG animation · ElevenLabs voiceover.</sub>
