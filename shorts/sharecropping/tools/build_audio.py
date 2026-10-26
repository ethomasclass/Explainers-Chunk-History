#!/usr/bin/env python3
"""Splice the Short's narration out of the voiced Reconstruction Ep 2 chapters, then mix music and sound effects.

Usage: python3 tools/build_audio.py [path/to/15minhistorystyle]

No new voice credits: every line is cut from ch08_no_land.wav / ch09_the_debt.wav using their words.json, the same
way the channel's Shorts are cut (0.12 s before the first word, 0.2 s after the last, 0.3 s of air between lines).

Writes, next to this folder:
  audio/narration.wav   the spliced voice alone
  audio/mix.wav         voice + music bed + sound effects (what the render uses)
  timeline.json         every spoken word with its time in the Short, plus the segment list and total length
  timeline.js           the same words for the page (window.TIMELINE)
"""
import json, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', '..', '15minhistorystyle')
EP2 = os.path.join(STYLE, 'projects', 'Reconstruction', 'ep2', 'public')
SR = 44100
PRE, POST, AIR = 0.12, 0.2, 0.25
LEAD = 0.25          # silence before the first line (frame 0 is the cover)
TAIL = 3.0           # the end card after the last line

# (chapter, first words, last words): phrases as written in the chapter's words.json
SEGMENTS = [
    ('ch09', 'the family finds', 'than it made.'),                     # hook, from the settling-up
    ('ch08', "It's called sharecropping.", "It's called sharecropping."),
    ('ch08', 'A family moves', 'with a cabin.'),
    ('ch08', 'The planter provides', 'provides the work.'),
    ('ch08', 'At harvest, they', 'half and half.'),
    ('ch09', 'until harvest, a', 'has to eat.'),
    ('ch09', 'So they bought', 'needed on credit.'),
    ('ch09', 'Usually from a', 'by the planter.'),
    ('ch09', 'they signed a', 'sees a cent.'),
    ('ch09', 'And at the', 'came settling up.'),
    ('ch09', 'The crop is', 'than it made.'),                      # the peak (the hook's own words, in context)
    ('ch09', 'That means they', "they can't leave."),
    ('ch09', 'So they sign', 'Then another.'),
    ('ch09', 'But for a', 'no way out.'),
]
FILES = {'ch08': 'ch08_no_land', 'ch09': 'ch09_the_debt'}


def decode(path, ch=1):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32)
    return a.reshape(-1, ch) if ch > 1 else a


def norm(w):
    return w.lower().strip('.,?!";:“”')


def find(words, phrase, nth=1, from_i=0):
    p = [norm(x) for x in phrase.split()]
    seen = 0
    for i in range(from_i, len(words) - len(p) + 1):
        if [norm(words[i + k]['w']) for k in range(len(p))] == p:
            seen += 1
            if seen == nth:
                return i
    raise SystemExit('phrase not found: %r' % phrase)


def loudness(path, target=-14.0):
    """Bring the mix up to about -14 LUFS. The voice's peaks run high for its loudness, so a plain gain (or master.py's
    linear pass) stalls near -15.6; a fast limiter at -1.5 dBTP shaves those few transients and lets the gain through."""
    p = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'loudnorm=print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True)
    m = json.loads(p.stderr[p.stderr.rindex('{'):])
    gain = target - float(m['input_i']) + 0.3                     # +0.3: the limiter takes a little back
    tmp = path + '.tmp.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-af',
                    'volume=%.2fdB,alimiter=limit=-1.5dB:attack=3:release=60:level=false' % gain,
                    '-c:a', 'pcm_s16le', tmp], check=True)
    os.replace(tmp, path)


def main():
    words = {k: json.load(open(os.path.join(EP2, 'audio', v + '.words.json')))['words'] for k, v in FILES.items()}
    audio = {k: decode(os.path.join(EP2, 'audio', v + '.wav')) for k, v in FILES.items()}

    out, tl, segs = [np.zeros(int(LEAD * SR), np.float32)], [], []
    t = LEAD
    for s in SEGMENTS:
        ch, first, last = s[:3]
        nth = s[3] if len(s) > 3 else 1
        W = words[ch]
        i0 = find(W, first)
        i1 = find(W, last, nth, i0) + len(last.split()) - 1
        a, b = W[i0]['s'] - PRE, W[i1]['e'] + POST
        clip = audio[ch][int(a * SR):int(b * SR)].copy()
        fade = int(0.01 * SR)
        clip[:fade] *= np.linspace(0, 1, fade)
        clip[-fade:] *= np.linspace(1, 0, fade)
        segs.append({'ch': ch, 'src': [round(a, 3), round(b, 3)], 'at': round(t, 3),
                     'text': ' '.join(w['w'] for w in W[i0:i1 + 1])})
        for w in W[i0:i1 + 1]:
            tl.append({'w': w['w'], 's': round(t + w['s'] - a, 3), 'e': round(t + w['e'] - a, 3)})
        out += [clip, np.zeros(int(AIR * SR), np.float32)]
        t += (b - a) + AIR
    out.append(np.zeros(int((TAIL - AIR) * SR), np.float32))
    vo = np.concatenate(out)
    total = len(vo) / SR

    # music: rc_codes (the trapped cue Ep 2 ch09 uses), ducked under the voice, cut just before "owes" at the peak,
    # back in for the aftermath, faded out under the end card
    def at(phrase, nth=1):
        p = [norm(x) for x in phrase.split()]
        hit = 0
        for i in range(len(tl) - len(p) + 1):
            if [norm(tl[i + k]['w']) for k in range(len(p))] == p:
                hit += 1
                if hit == nth:
                    return tl[i]['s']
        raise SystemExit('cue not found: %r' % phrase)

    mus = decode(os.path.join(EP2, 'music', 'rc_codes.mp3'), 2).mean(axis=1)
    bed = np.zeros_like(vo)
    n = min(len(bed), len(mus))
    bed[:n] = mus[:n]
    if len(bed) > len(mus):                                     # loop once if the cue is shorter than the Short
        bed[len(mus):] = mus[:len(bed) - len(mus)]
    env = np.full(len(bed), 0.17, np.float32)
    drop, back = at('owes', 2) - 0.13, at("That means")
    k = lambda x: int(x * SR)
    env[k(drop - 1.2):k(drop)] = np.linspace(0.17, 0, k(drop) - k(drop - 1.2))
    env[k(drop):k(back)] = 0
    env[k(back):k(back + 1.5)] = np.linspace(0, 0.17, k(back + 1.5) - k(back))
    env[k(total - 3):] = np.linspace(0.17, 0, len(env) - k(total - 3))
    env[:k(0.4)] = np.linspace(0, 0.17, k(0.4))
    mix = vo + bed * env

    sfx = lambda name: decode(os.path.join(EP2, 'sfx', name + '.wav'), 2).mean(axis=1)
    hits = [('stamp', at('sharecropping.'), 0.5), ('whoosh', at('A family moves') - 0.3, 0.35),
            ('page_turn', at('they signed') - 0.2, 0.4), ('stamp', at('came settling') + 0.5, 0.45),
            ('marker_tick', at('The crop is'), 0.3), ('marker_tick', at("family's half"), 0.3),
            ('marker_tick', at('Then the store'), 0.3), ('marker_tick', at('plus interest'), 0.3),
            ('page_turn', at('another year'), 0.4), ('page_turn', at('Then another.'), 0.4),
            ('stamp', total - TAIL + 0.15, 0.45)]
    for name, when, vol in hits:
        s = sfx(name)
        i = k(when)
        mix[i:i + len(s)] += s[:len(mix) - i] * vol

    peak = np.abs(mix).max()
    if peak > 0.98:
        mix *= 0.98 / peak

    def write(path, a):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-',
                        '-c:a', 'pcm_s16le', path], input=a.astype(np.float32).tobytes(), check=True)

    os.makedirs(os.path.join(HERE, 'audio'), exist_ok=True)
    write(os.path.join(HERE, 'audio', 'narration.wav'), vo)
    write(os.path.join(HERE, 'audio', 'mix.wav'), mix)
    loudness(os.path.join(HERE, 'audio', 'mix.wav'))
    json.dump({'duration': round(total, 3), 'segments': segs, 'words': tl},
              open(os.path.join(HERE, 'timeline.json'), 'w'), indent=1)
    with open(os.path.join(HERE, 'timeline.js'), 'w') as f:                # the page loads this (works from file://)
        f.write('window.TIMELINE = ' + json.dumps({'duration': round(total, 3), 'words': tl}) + ';\n')
    print('Short: %.2f s, %d segments, %d words' % (total, len(segs), len(tl)))
    for s in segs:
        print('  %6.2f  %s' % (s['at'], s['text']))


if __name__ == '__main__':
    main()
