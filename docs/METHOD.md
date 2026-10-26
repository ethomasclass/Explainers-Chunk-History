# The Method

How to build a produced-quality animated explainer video as one self-contained HTML file. This is the human-readable narrative; the two `SKILL.md` files are the exhaustive references. The pipeline is seven stages:

**script → scaffold → choreography → retention pass → VO-sync → zero-overlap gates → voiceover**

---

## 0. The mental model

A finished explainer is not a slideshow. It has a **layered world** (parallax sky/hills/foreground), a **camera** (vignette, grain, push-ins, dolly), a **cast** (a flying host mascot plus a population of little characters), and **choreography that feels physical** (things drop with weight, collide, dodge, fuse). All of that is already wired into `scaffold.html`. Your job is to swap in *your* content scene by scene, adapting the proven patterns rather than inventing motion from scratch.

The stage is a fixed **800×500** coordinate space scaled to fit its container. Each scene is a `<div class="xpl-scene" data-scene="i">`. Four parallel arrays, keyed by scene index, drive everything:

- `SCENES[i]` — seconds the scene is on screen (last entry `999` = the CTA holds).
- `FL[i]` — the host's flight plan: `[[fraction, x, y, pointing], ...]`.
- `ACTS[i]` — a function building that scene's GSAP timeline.
- `CH_STARTS` — which scenes get a chapter tick on the seek bar.

Keep those four in sync after any add/remove. Text and captions enter with cheap CSS primitives (`.fu` fade-up, `.pp` pop, `.fi` fade-in) via inline `animation-delay`; the hero choreography is GSAP. One element has exactly one owner — never put a `.fu` class on a GSAP-driven element.

## 1. Script first

Write a shot script as Markdown *before* touching the HTML. Per scene: timestamp, duration, VISUAL, ON-SCREEN text, and the VO line. End with an accuracy checklist and verify every factual claim. This doc is load-bearing later: the durations become `SCENES`, and the VO lines become the `sr-only` transcript (which doubles as the recording script). Ground the topic in whatever demand signal you have (search-gap data, comments, FAQ).

## 2. Scaffold

Copy `scaffold.html` to `<topic>.html`. Run `python3 inline-gsap.py <topic>.html` once — it fetches GSAP 3.13 (core + the full free plugin suite) from the public CDN into a gitignored `vendor/` and inlines it at the `<!--GSAP_INLINE-->` marker. Open the file; it must play before you change anything.

Then replace scenes **one at a time**, keeping the five worked examples as your idiom source until each is gone:

- **S0** — dark cold-open hook with a flip-reveal (a tempting ✓ that swaps for ✗).
- **S1** — drop-with-bounce physics (objects fall into a vessel with weight).
- **S2** — a pour: a container rotates, its contents arc out on motion paths, land, and fuse into a new shape drawn with DrawSVG.
- **S3** — the **forced-overlap collision** — the peak. Two bars drop into one track that can't hold both; the second tries to dodge, fails, and the overlap glows. This is the pattern that carries the video.
- **S4** — the CTA hold.

## 3. Choreography (adapt, don't invent)

Every pattern you need already exists verbatim in the scaffold. The high-value ones:

- **Drop with weight** — `CustomBounce` gives paired eases; the object falls *and* squashes on impact (`scaleX:1.45, scaleY:.55`). The squash is the weight. Strictly better than a plain `bounce.out`.
- **Forced-overlap collision** — intent → failure → consequence. The second bar *tries* to move aside (an `x` yoyo), can't, settles; then the overlap segment pops and pulses; then two "both-badge" characters appear inside it. The attempt is what makes it feel alive.
- **MorphSVG fuse** — the single most Kurzgesagt move: N objects land in a row, a silhouette path fades in over them, then morphs to the concept (an arrow, a symbol) while the fill re-colors.
- **Population as characters** — quantities are little characters (`minion()`), not dots. Ambient ones drift through the margins; the proof moment is characters wearing both badges.
- **Host flight** — the mascot flies between waypoints; long legs auto-swoop along a curve; on arrival it points and taps. Each scene's first waypoint equals the previous scene's last, so cuts are seamless.

Deterministic reset is the discipline that makes all of this survive replay and seek: **every `ACTS[i]` begins with `gsap.set(...)` resets** for every property it will touch — including infinite `repeat:-1` glows and any 1px yoyo axis. A killed tween leaves stale inline styles; the reset is what a re-entered scene starts from.

Craft note: props stop looking like styled divs when you give them **two-tone shading** (a gradient body plus inset gloss/shade box-shadows), **one consistent light direction** film-wide, and a **drop-shadow filter on line art** so strokes reveal with a lit underside as DrawSVG draws them.

## 4. Retention pass (before VO)

Run this *before* recording voiceover, while durations are still free to change. Three rounds:

1. **Structure.** Audit the hook/peak loop: what does the first visual literally show, and does the peak visually rhyme with it? If not, recut the cold open from the peak scene's own prop classes, held as a question. Then **trim every scene to its choreography** — the last content beat should land at 70–85% of the scene's duration. (In practice, scenes overrun their choreography by 30–100% by default. Expect to cut a quarter of the runtime with zero content loss.)
2. **Beat coverage.** Map choreography against durations with `node beat-audit.mjs <file>`. For any scene under 60% coverage or with a >4s gap, add a *content* B-beat — ideally by moving an existing late beat later, or a callback pulse reusing the scene's own props. Never pad with ambient motion.
3. **Polish.** Add stakes accents late in long scenes, one pattern interrupt at each predicted drop point (~30%, ~60%), name the loop closures explicitly, and give the last content scene exit velocity into the CTA.

When you trim a scene, remember trims strand three kinds of absolute values in the same breath — late `ACTS` beat times, CSS `animation-delay`s, and any on-page duration labels. Retime all three in the same edit.

## 5. VO-sync — "say it = show it"

Walk the transcript sentence by sentence and confirm the named object has a beat within ±1.5s of its name. Two defects show up in nearly every first draft:

- **Enumerations dump early.** Four items all land in the first few seconds while the narrator names them across fifteen. Re-space each item's entrance to its name.
- **Payoffs resolve before their reasoning.** A ✓ that stamps before the argument finishes spoils the peak. Gate every winner-stamp and shatter to the phrase that earns it.

Any phrase that asserts a mechanism deserves a dedicated 3–6s mini-diagram, not a caption. Longer-and-taught beats shorter-and-asserted.

## 6. Zero-overlap gates

Before publishing, run the pre-publish gates: `node --check` the last script block; confirm every script-targeted class resolves; run the replay-reset audit (interrupt mid-beat, re-enter, read back every animated property); and run the **pairwise overlap auditor** (`tools/overlap-audit.js`).

The rule: *nothing overlaps anything unless the overlap is the lesson.* No words on words, the host on nothing ever, arrows never crossing text, ambient characters out of text bands. Deliberate teaching overlaps get `data-ovl-ok="sharedToken"` on both elements. **Sample at 0.5s steps** — coarser sampling misses fast host flights that strike a headline mid-transit. The auditor exists because a frozen preview reports CSS-entrance elements at opacity 0, so a naive box sweep silently excludes half the content; the tool forces each element visible per its own delay before measuring.

## 7. Voiceover

The master stays silent — you screen-record it and lay VO in post, or ship a separate `-vo.html` variant with per-scene clips embedded.

Write the script at **~2.5 words/sec × scene duration** (a cloned/TTS voice reads ~2.6 w/s; overestimating pace is why clips overrun). Aim for 85–94% fill — continuous narration with a natural breath at each cut. Every phrase should narrate a beat on screen; no filler.

Generate one clip per scene and check its length against the scene:

```bash
export ELEVENLABS_API_KEY=...     # or ./.env
python3 tools/vo-generate.py <script.md> ./vo <voiceId>
```

It prints each clip's duration vs `SCENES[i]` and flags overruns. **Extend** any scene its clip overran (clip + 1.5–2s) rather than trimming — extending never strands choreography; trimming does. Then embed the clips as a base64 `VO[]` array played from `showScene(i)`, wired into pause/resume, with the first click as the autoplay gesture.

## Publishing

Everything is inline, so the file is portable and CSP-safe — open it, host it, or embed it anywhere. For YouTube: screen-record fullscreen playback, lay the VO, export. For Shorts: seek to a chapter and record that scene range at a 9:16 crop.

---

### The gotchas that cost real time

- GSAP must be **inline** for a self-contained file (CDNs are blocked by CSP). `inline-gsap.py` handles it.
- Never `new SplitText` inside a scene function — it nests spans on every replay. Split once via a registry.
- Relative `'+=n'` tweens only stay put across replays with wiggle eases (they return to start); otherwise the reset must zero the axis.
- Entrances animate the `translate`/`scale`/`rotate` properties; idle loops animate the `transform` shorthand — mixing them clobbers centering.
- On an SVG group, a px `transformOrigin` is bounding-box-relative; use `svgOrigin:'x y'` for a fixed pivot in SVG coordinates.
- Include `<meta charset="utf-8">` or a local `http.server` serves the file as latin-1 and your symbols mojibake.
- The final `SCENES` entry is `999` and the clock must call `done()` on it, or the play/pause toggle sticks.
