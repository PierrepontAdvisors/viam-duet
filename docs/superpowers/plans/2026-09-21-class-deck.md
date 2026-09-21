# Class deck ("A robot that draws back") Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A fourteen-card HTML deck at `docs/duet/class/` plus a talk-track, for Nicholas's ~20-minute Zoom talk to Carolina Uribe's 9th–12th grade Python class, with a real ten-card `?cut=10` version.

**Architecture:** One static page that reuses the pitch deck's stylesheet, font, developer mode and images by relative path (`../pitch/`), adds `class.css` for the new card types and `class.js` for navigation (pure state functions on `window.ClassDeck`, DOM wiring guarded so Node can load the file). Assets with identifiable people and other teams' clips are built locally by `build_assets.py` and kept out of git. Tests mirror the pitch's `pagetests/pitch.test.mjs`.

**Tech Stack:** Plain HTML/CSS/JS (classic script, works over `file://`), Node's built-in test runner (`node --test`), Python 3.12 + Pillow 12 + ffmpeg 9 for assets, pytest for the asset script.

**Spec:** `docs/superpowers/specs/2026-09-21-class-deck-design.md`. Read it first. Read `docs/duet/pitch/index.html`, `deck.css`, `deck.js` and `code/hackathon/pagetests/pitch.test.mjs` before Task 2: the class deck copies their conventions exactly.

**Working directory:** the worktree `.worktrees/class-deck` on branch `feat/class-deck`. Run every command from there. Node tests run from `code/hackathon`; the Python venv is `code/hackathon/.venv`. Never `git add -A`; add files by name. Never commit `docs/duet/class/video/`, `img/crowd.jpg`, `img/medal.jpg`, `.claude/launch.json`, or `hackathon-videos/` (all gitignored; the ignore rules landed with the spec commit).

---

## File structure

| File | Responsibility |
|---|---|
| `docs/duet/class/index.html` | The fourteen cards, SVG defs (squiggle patterns, logo), links to `../pitch/fredoka.css`, `../pitch/deck.css`, `class.css`, `class.js`, `../pitch/dev.js` |
| `docs/duet/class/class.css` | Only what `deck.css` lacks: reveals, the `half` template, and one block per new card type |
| `docs/duet/class/class.js` | Navigation for a deck whose card count comes from the page; `?cut=10`; reveals; flipbook and clip playback tied to the shown card |
| `docs/duet/class/build_assets.py` | Photos and clips from `hackathon-videos/` into `img/` and `video/`, idempotent |
| `docs/duet/class/talk.md` | Pre-flight, per-card spoken words with times, the 10-minute version, likely questions |
| `docs/duet/class/README.md` | How to open it, keys, `?cut=10`, `?notes=1`, assets, what is local-only |
| `docs/duet/class/img/` | `setup.jpg`, `door.jpg` (committed); `crowd.jpg`, `medal.jpg` (local-only) |
| `docs/duet/class/video/` | `team-1.mp4` … `team-4.mp4` (local-only) |
| `code/hackathon/pagetests/class.test.mjs` | Node tests for the deck |
| `code/hackathon/tests/test_class_assets.py` | pytest for `build_assets.py`'s job table |
| `.claude/launch.json` (worktree, untracked) | `class` entry serving `docs/duet` on 8792 for browser checks |

---

### Task 1: Align the spec's on-card code with what fits, and build the local assets

**Files:**
- Modify: `docs/superpowers/specs/2026-09-21-class-deck-design.md` (card 6 captions, card 7 right panel, card 11 excerpt)
- Create: `docs/duet/class/build_assets.py`
- Create: `code/hackathon/tests/test_class_assets.py`

Two on-card code blocks in the spec are wider than their panels (a 47-character turtle line at 1.8cqw monospace is 56cqw; the panel is about 42cqw). The talk does not change; the on-card text does.

- [ ] **Step 1: Update the spec's card 6 captions, card 7 panels and card 11 excerpt**

In the spec, replace card 6's two captions: `(caption "the camera takes a photo")` stays; change `(caption "the sentence becomes a list of points, and the arm follows them")` to `(caption "the arm follows the points")`.

Replace the two code blocks under card 7 with exactly:

Left, "Your turtle":
```python
import turtle
t = turtle.Turtle()
points = [(40, 0), (40, 40),
          (0, 40), (0, 0)]
t.penup()
t.goto(0, 0)
t.pendown()
for x, y in points:
    t.goto(x, y)
t.penup()
```
Right, "My robot (simplified)":
```python
stroke = points_from_claude()
# e.g. [(0, 0), (40, 0), (40, 40)]
x, y = stroke[0]
pen_up()
move_to(x, y)
pen_down()
for x, y in stroke[1:]:
    move_to(x, y)
pen_up()
```

Replace card 11's four-line excerpt with:
```
class Palletizer:
    def obstacles(self):
        boxes = self.placed_boxes()
    return WorldState(boxes)
```

- [ ] **Step 2: Write the failing pytest for the asset script's job table**

Create `code/hackathon/tests/test_class_assets.py`:

```python
"""build_assets.py (docs/duet/class) plans its conversions from a fixed table and skips existing outputs."""
import importlib.util
import pathlib

SCRIPT = pathlib.Path(__file__).resolve().parents[3] / "docs" / "duet" / "class" / "build_assets.py"
REPO = SCRIPT.parents[3]


def load():
    spec = importlib.util.spec_from_file_location("build_assets", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_jobs_skips_existing_outputs_unless_forced():
    m = load()
    every = [dst for _, dst in m.PHOTOS + m.CLIPS]
    assert m.jobs(set(every), force=False) == []
    assert [d for _, _, d in m.jobs(set(every), force=True)] == every
    assert [d for _, _, d in m.jobs(set(every) - {"video/team-2.mp4"}, force=False)] == ["video/team-2.mp4"]
    assert [k for k, _, _ in m.jobs(set(), force=False)] == ["photo"] * 4 + ["clip"] * 4


def test_table_is_the_spec_table():
    m = load()
    assert m.PHOTOS == [
        ("photo-setup.webp", "img/setup.jpg"),
        ("photo-door.webp", "img/door.jpg"),
        ("photo-crowd.webp", "img/crowd.jpg"),
        ("photo-medal.jpg", "img/medal.jpg"),
    ]
    assert [s for s, _ in m.CLIPS] == ["IMG_0016.MOV", "IMG_0018.mov", "IMG_0022.mov", "IMG_0024.mov"]
    assert [d for _, d in m.CLIPS] == [f"video/team-{n}.mp4" for n in (1, 2, 3, 4)]
    assert (m.MAX_SIDE, m.JPEG_QUALITY, m.CLIP_HEIGHT, m.CLIP_SECONDS) == (2000, 85, 720, 15)


def test_local_only_outputs_and_the_source_folder_are_gitignored():
    lines = (REPO / ".gitignore").read_text().splitlines()
    for rule in ["hackathon-videos/", "docs/duet/class/video/", "docs/duet/class/img/crowd.jpg", "docs/duet/class/img/medal.jpg"]:
        assert rule in lines, rule
```

- [ ] **Step 3: Run it to see it fail**

Run (from `code/hackathon`): `.venv/bin/python -m pytest -q tests/test_class_assets.py`
Expected: 3 failed, `FileNotFoundError` or `AttributeError` (the script does not exist).

- [ ] **Step 4: Write `build_assets.py`**

Create `docs/duet/class/build_assets.py`:

```python
#!/usr/bin/env python3
"""Build the class deck's local assets from hackathon-videos/ at the repo root.

Photos: webp or jpg -> img/*.jpg, longest side 2000 px, JPEG quality 85 (Pillow).
Clips:  .mov -> video/team-N.mp4, H.264, 720 px tall, no audio, at most 15 s (ffmpeg).
Outputs that exist are skipped; --force redoes them. Sources that are missing are reported, not fatal,
so the deck builds without the medal photo until it is dropped in.

Run with the hackathon venv:  ../../../code/hackathon/.venv/bin/python build_assets.py
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[2] / "hackathon-videos"          # docs/duet/class -> repo root
MAX_SIDE = 2000
JPEG_QUALITY = 85
CLIP_HEIGHT = 720
CLIP_SECONDS = 15

PHOTOS = [
    ("photo-setup.webp", "img/setup.jpg"),
    ("photo-door.webp", "img/door.jpg"),
    ("photo-crowd.webp", "img/crowd.jpg"),
    ("photo-medal.jpg", "img/medal.jpg"),
]
CLIPS = [                                             # clip order is chronological by filename
    ("IMG_0016.MOV", "video/team-1.mp4"),
    ("IMG_0018.mov", "video/team-2.mp4"),
    ("IMG_0022.mov", "video/team-3.mp4"),
    ("IMG_0024.mov", "video/team-4.mp4"),
]


def jobs(existing: set[str], force: bool) -> list[tuple[str, str, str]]:
    """(kind, src, dst) for every output not in `existing`, or all of them with force. Photos first."""
    out: list[tuple[str, str, str]] = []
    for kind, table in (("photo", PHOTOS), ("clip", CLIPS)):
        for src, dst in table:
            if force or dst not in existing:
                out.append((kind, src, dst))
    return out


def convert_photo(src: Path, dst: Path) -> None:
    from PIL import Image, ImageOps

    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((MAX_SIDE, MAX_SIDE))
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst, "JPEG", quality=JPEG_QUALITY, optimize=True)


def convert_clip(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-t", str(CLIP_SECONDS),
         "-vf", f"scale=-2:{CLIP_HEIGHT}", "-c:v", "libx264", "-crf", "23", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", str(dst)],
        check=True,
    )


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="redo outputs that already exist")
    args = ap.parse_args(argv)
    existing = {dst for _, dst in PHOTOS + CLIPS if (HERE / dst).exists()}
    todo = jobs(existing, args.force)
    if not todo:
        print("nothing to do")
        return 0
    missing: list[str] = []
    for kind, src, dst in todo:
        source = SRC / src
        if not source.exists():
            missing.append(src)
            continue
        print(f"{kind}: {src} -> {dst}")
        (convert_photo if kind == "photo" else convert_clip)(source, HERE / dst)
    for name in missing:
        print(f"skipped, source not found: {SRC / name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 5: Run the pytest to see it pass**

Run (from `code/hackathon`): `.venv/bin/python -m pytest -q tests/test_class_assets.py`
Expected: `3 passed`.

- [ ] **Step 6: Build the assets**

Run (from `docs/duet/class`): `../../../code/hackathon/.venv/bin/python build_assets.py`
Expected: seven `photo:`/`clip:` lines, then `skipped, source not found: .../hackathon-videos/photo-medal.jpg` on stderr if Nicholas has not dropped the medal photo in yet. Then:

Run: `ls -la img video && for f in video/*.mp4; do ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration -of csv=p=0 "$f"; done`
Expected: `setup.jpg`, `door.jpg`, `crowd.jpg` (and `medal.jpg` if present) under 1 MB each; four mp4s reporting `406,720,<=15.1` (ffmpeg rounds the width to an even number).

Run: `git status --short`
Expected: the spec, `build_assets.py` and the test show; `img/setup.jpg` and `img/door.jpg` show as untracked; nothing under `video/`, no `crowd.jpg`, no `medal.jpg` (ignored).

- [ ] **Step 7: Commit**

```bash
git add docs/superpowers/specs/2026-09-21-class-deck-design.md docs/duet/class/build_assets.py code/hackathon/tests/test_class_assets.py docs/duet/class/img/setup.jpg docs/duet/class/img/door.jpg
git commit -m "feat(class): asset build script and the two committed photos

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: `class.js` — pure navigation for a page-sized deck, and its tests

**Files:**
- Create: `docs/duet/class/class.js`
- Create: `code/hackathon/pagetests/class.test.mjs`

`deck.js` hardcodes `CARDS = 7` and carries the pitch's autoplay and notes pills. `class.js` is its own file: the pure functions take a `deck` (`{ cards, builds }`) so the `?cut=10` deck is just a different object; the DOM wiring builds that object from the page.

- [ ] **Step 1: Write the failing tests for the pure functions**

Create `code/hackathon/pagetests/class.test.mjs`:

```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

// pagetests/ -> code/hackathon/ -> Viam/ -> docs/duet/class/
const DIR = fileURLToPath(new URL('../../../docs/duet/class/', import.meta.url));
const ROOT = fileURLToPath(new URL('../../../', import.meta.url));
const read = (name) => readFileSync(DIR + name, 'utf8');

const TURNS = 10;
const FLIPBOOK = ['turn-00-start.jpg',
  ...Array.from({ length: TURNS }, (_, i) => String(i + 1).padStart(2, '0'))
    .flatMap((nn) => [`turn-${nn}-human.jpg`, `turn-${nn}-robot.jpg`])];

// the fourteen cards as class.js reads them from the page: which are cut at ten minutes, and how many reveals each has
const SPECS = [
  { cut: '', builds: 0 }, { cut: '', builds: 0 }, { cut: '20', builds: 0 }, { cut: '', builds: 4 },
  { cut: '', builds: 4 }, { cut: '', builds: 3 }, { cut: '', builds: 0 }, { cut: '', builds: 0 },
  { cut: '20', builds: 0 }, { cut: '', builds: 0 }, { cut: '20', builds: 0 }, { cut: '20', builds: 0 },
  { cut: '', builds: 0 }, { cut: '', builds: 2 },
];

// class.js is a classic script for file://; Node runs it with a bare `window` and no `document`,
// which also proves the DOM wiring is guarded. Same realm, so deepEqual can compare its objects.
function loadDeck() {
  const window = {};
  new Function('window', read('class.js'))(window);
  return window.ClassDeck;
}

test('the full deck is fourteen cards with reveals on 4, 5, 6 and 14; the cut keeps ten and renumbers the reveals', () => {
  const D = loadDeck();
  assert.deepEqual(D.deckOf(D.keep(SPECS, 0)), { cards: 14, builds: { 4: 4, 5: 4, 6: 3, 14: 2 } });
  assert.deepEqual(D.deckOf(D.keep(SPECS, 10)), { cards: 10, builds: { 3: 4, 4: 4, 5: 3, 10: 2 } });
  assert.equal(D.keep(SPECS, 10).length, 10);
  assert.equal(D.parseCut(''), 0);
  assert.equal(D.parseCut('?cut=10'), 10);
  assert.equal(D.parseCut('?notes=1&cut=10'), 10);
  assert.equal(D.parseCut('?cut=20'), 0);
  assert.equal(D.parseCut(undefined), 0);
});

test('renumber rewrites the two-digit prefix of a kicker', () => {
  const D = loadDeck();
  assert.equal(D.renumber('04 · Why I built this', 3), '03 · Why I built this');
  assert.equal(D.renumber('14 · One piece of advice', 10), '10 · One piece of advice');
  assert.equal(D.renumber('01 · Duet', 1), '01 · Duet');
});

test('advance reveals card 4 one line at a time, then moves on', () => {
  const D = loadDeck();
  const deck = D.deckOf(D.keep(SPECS, 0));
  let s = { card: 4, build: 0 };
  s = D.advance(s, deck); assert.deepEqual(s, { card: 4, build: 1 });
  s = D.advance(s, deck); assert.deepEqual(s, { card: 4, build: 2 });
  s = D.advance(s, deck); assert.deepEqual(s, { card: 4, build: 3 });
  s = D.advance(s, deck); assert.deepEqual(s, { card: 4, build: 4 });
  s = D.advance(s, deck); assert.deepEqual(s, { card: 5, build: 0 });
  assert.deepEqual(D.advance({ card: 1, build: 0 }, deck), { card: 2, build: 0 });
});

test('advance stops on the last card of either deck and never mutates its input', () => {
  const D = loadDeck();
  const full = D.deckOf(D.keep(SPECS, 0));
  const cut = D.deckOf(D.keep(SPECS, 10));
  const last14 = Object.freeze({ card: 14, build: 2 });
  assert.equal(D.advance(last14, full), last14);
  const last10 = Object.freeze({ card: 10, build: 2 });
  assert.equal(D.advance(last10, cut), last10);
  assert.deepEqual(D.advance({ card: 10, build: 0 }, full), { card: 11, build: 0 });
  const first = Object.freeze({ card: 1, build: 0 });
  D.advance(first, full);
  assert.deepEqual(first, { card: 1, build: 0 });
});

test('back hides the latest reveal, and from the next card lands on the previous one fully revealed', () => {
  const D = loadDeck();
  const deck = D.deckOf(D.keep(SPECS, 0));
  assert.deepEqual(D.back({ card: 4, build: 2 }, deck), { card: 4, build: 1 });
  assert.deepEqual(D.back({ card: 5, build: 0 }, deck), { card: 4, build: 4 });
  assert.deepEqual(D.back({ card: 7, build: 0 }, deck), { card: 6, build: 3 });
  assert.deepEqual(D.back({ card: 9, build: 0 }, deck), { card: 8, build: 0 });
  const start = { card: 1, build: 0 };
  assert.equal(D.back(start, deck), start);
});

test('jump clamps to the deck and starts that card unrevealed; parseHash reads #n', () => {
  const D = loadDeck();
  const full = D.deckOf(D.keep(SPECS, 0));
  const cut = D.deckOf(D.keep(SPECS, 10));
  assert.deepEqual(D.jump(6, full), { card: 6, build: 0 });
  assert.deepEqual(D.jump(0, full), { card: 1, build: 0 });
  assert.deepEqual(D.jump(99, full), { card: 14, build: 0 });
  assert.deepEqual(D.jump(14, cut), { card: 10, build: 0 });
  assert.equal(D.parseHash('#3', full), 3);
  assert.equal(D.parseHash('#12', cut), 10);
  assert.equal(D.parseHash('', full), 1);
  assert.equal(D.parseHash('#nope', full), 1);
  assert.equal(D.parseHash(undefined, full), 1);
});

test('notes are off unless ?notes=1 (a screen-share must not show them)', () => {
  const D = loadDeck();
  assert.equal(D.parseNotes(''), false);
  assert.equal(D.parseNotes('?cut=10'), false);
  assert.equal(D.parseNotes('?notes=1'), true);
  assert.equal(D.parseNotes('?cut=10&notes=1'), true);
  assert.equal(D.parseNotes('?notes=0'), false);
});

test('the flipbook lists the 21 pitch photos in turn order, labels them, and holds on the last', () => {
  const D = loadDeck();
  assert.deepEqual(D.FLIPBOOK, FLIPBOOK);
  assert.equal(D.PITCH_IMG, '../pitch/img/');
  assert.equal(D.flipLabel(0), 'start');
  assert.equal(D.flipLabel(1), 'turn 1 of 10 · you');
  assert.equal(D.flipLabel(2), 'turn 1 of 10 · Duet');
  assert.equal(D.flipLabel(20), 'turn 10 of 10 · Duet');
  assert.equal(D.flipDelay(0), 700);
  assert.equal(D.flipDelay(20), 2000);
  assert.equal(D.nextFlip(3), 4);
  assert.equal(D.nextFlip(20), 0);
  for (const f of FLIPBOOK) assert.ok(existsSync(DIR + '../pitch/img/' + f), `pitch photo missing: ${f}`);
});

test('the wiring: cut prunes and renumbers cards, reveals follow data-step, media runs only on its card, keys 1-9 and 0', () => {
  const js = read('class.js');
  assert.match(js, /if \(typeof document === 'undefined'\) return;/);
  assert.match(js, /parseCut\(location\.search\)/);
  assert.match(js, /el\.parentNode\.removeChild\(el\)/);
  assert.match(js, /setAttribute\('data-card', String\(i \+ 1\)\)/);
  assert.match(js, /renumber\(k\.textContent, i \+ 1\)/);
  assert.match(js, /querySelectorAll\('\[data-step\]'\)/);
  assert.match(js, /classList\.toggle\('shown'/);
  assert.match(js, /v\.play\(\)/);
  assert.match(js, /v\.pause\(\)/);
  assert.match(js, /clearTimeout\(flipTimer\)/);
  assert.match(js, /case '0': set\(jump\(10, deck\)\); return;/);
  assert.match(js, /\/\^\[1-9\]\$\//);
  assert.match(js, /case 'f': case 'F': toggleFullscreen\(\); return;/);
  assert.match(js, /stage\.classList\.toggle\('shownotes', parseNotes\(location\.search\)\)/);
  assert.ok(!/case 'p':/.test(js) && !/case 'n':/.test(js), 'no autoplay or notes keys: the class deck is only ever talked through');
  assert.ok(!/id="play"|getElementById\('play'\)/.test(js), 'no play button');
});
```

- [ ] **Step 2: Run the tests to see them fail**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: every test fails with `ENOENT ... class.js`.

- [ ] **Step 3: Write `class.js`**

Create `docs/duet/class/class.js`:

```js
/* Duet class deck. A classic script so it runs over file:// in Chrome; the pure state functions
   hang off window.ClassDeck so the Node tests can load this file without a DOM. Unlike deck.js
   the card count comes from the page (?cut=10 drops the cards marked data-cut="20"), so every
   pure function takes the deck it works on. */
(function () {
  'use strict';

  var PITCH_IMG = '../pitch/img/';     // the flipbook photos live with the pitch deck
  var FLIP_MS = 700;                   // per flipbook photo
  var FLIP_HOLD_MS = 2000;             // on the finished piece
  var TURNS = 10;                      // exchanges in the flipbook session
  var FLIPBOOK = ['turn-00-start.jpg'];
  for (var n = 1; n <= TURNS; n++) {
    var nn = (n < 10 ? '0' : '') + n;
    FLIPBOOK.push('turn-' + nn + '-human.jpg', 'turn-' + nn + '-robot.jpg');
  }

  /* ---- the deck: a card count and the reveal steps per card ---- */
  function parseCut(search) {          // ?cut=10 is the ten-minute version; anything else is the full deck
    var m = /[?&]cut=(\d+)/.exec(search || '');
    return m && m[1] === '10' ? 10 : 0;
  }
  function parseNotes(search) {        // rehearsal only: ?notes=1 shows the asides, nothing else does
    var m = /[?&]notes=([^&]*)/.exec(search || '');
    return !!(m && m[1] === '1');
  }
  function keep(specs, cut) {          // specs: [{cut: '20' | '', builds: k}] in page order
    return specs.filter(function (c) { return !(cut === 10 && c.cut === '20'); });
  }
  function deckOf(specs) {
    var builds = {};
    specs.forEach(function (c, i) { if (c.builds) builds[i + 1] = c.builds; });
    return { cards: specs.length, builds: builds };
  }
  function renumber(kicker, card) {    // "04 · Why I built this" becomes "03 · ..." in the cut
    return (card < 10 ? '0' : '') + card + kicker.slice(2);
  }

  function clamp(card, deck) { return Math.min(deck.cards, Math.max(1, card)); }
  function builds(card, deck) { return deck.builds[card] || 0; }

  function advance(s, deck) {
    if (s.build < builds(s.card, deck)) return { card: s.card, build: s.build + 1 };
    if (s.card < deck.cards) return { card: s.card + 1, build: 0 };
    return s;
  }
  function back(s, deck) {
    if (s.build > 0) return { card: s.card, build: s.build - 1 };
    if (s.card > 1) return { card: s.card - 1, build: builds(s.card - 1, deck) };
    return s;
  }
  function jump(card, deck) { return { card: clamp(card, deck), build: 0 }; }
  function parseHash(hash, deck) {
    var m = /^#(\d+)$/.exec(hash || '');
    return m ? clamp(parseInt(m[1], 10), deck) : 1;
  }
  function flipLabel(i) {
    if (i === 0) return 'start';
    return 'turn ' + Math.ceil(i / 2) + ' of ' + TURNS + ' · ' + (i % 2 ? 'you' : 'Duet');
  }
  function flipDelay(i) { return i === FLIPBOOK.length - 1 ? FLIP_HOLD_MS : FLIP_MS; }
  function nextFlip(i) { return (i + 1) % FLIPBOOK.length; }

  window.ClassDeck = {
    PITCH_IMG: PITCH_IMG, FLIPBOOK: FLIPBOOK,
    parseCut: parseCut, parseNotes: parseNotes, keep: keep, deckOf: deckOf, renumber: renumber,
    advance: advance, back: back, jump: jump, parseHash: parseHash,
    flipLabel: flipLabel, flipDelay: flipDelay, nextFlip: nextFlip
  };

  if (typeof document === 'undefined') return;   // Node tests stop here

  /* ---- wiring ---- */
  var deck, state = { card: 1, build: 0 };
  var stage, cards, counters, flipImg, flipLabelEl, flipCard, flipTimer = null, videos;

  function specOf(el) {
    return { cut: el.getAttribute('data-cut') || '', builds: parseInt(el.getAttribute('data-builds') || '0', 10) };
  }
  /* drop the cut cards from the page, then number what is left: data-card, the kicker prefix, the counter */
  function setup(cut) {
    var all = Array.prototype.slice.call(document.querySelectorAll('.card'));
    cards = [];
    all.forEach(function (el) {
      if (keep([specOf(el)], cut).length) cards.push(el); else el.parentNode.removeChild(el);
    });
    cards.forEach(function (el, i) {
      el.setAttribute('data-card', String(i + 1));
      var k = el.querySelector('.kicker');
      if (k) k.textContent = renumber(k.textContent, i + 1);
    });
    deck = deckOf(cards.map(specOf));
  }

  function render() {
    cards.forEach(function (el, i) {
      var active = i + 1 === state.card;
      el.classList.toggle('active', active);
      if (active) el.setAttribute('data-build', String(state.build));
      Array.prototype.forEach.call(el.querySelectorAll('[data-step]'), function (r) {
        r.classList.toggle('shown', active && parseInt(r.getAttribute('data-step'), 10) <= state.build);
      });
    });
    counters.forEach(function (el) { el.textContent = state.card + ' / ' + deck.cards; });
    if (parseHash(location.hash, deck) !== state.card) history.replaceState(null, '', '#' + state.card);
    media();
  }
  function set(next) {
    if (next === state) return;
    state = next;
    render();
  }

  /* the flipbook and the four clips run only while their card is up */
  function media() {
    var flipping = !!flipCard && flipCard.classList.contains('active');
    if (flipping && flipTimer === null) runFlipbook();
    if (!flipping && flipTimer !== null) { clearTimeout(flipTimer); flipTimer = null; }
    videos.forEach(function (v) {
      var up = v.closest('.card').classList.contains('active');
      if (up) { var p = v.play(); if (p && p.catch) p.catch(function () {}); } else v.pause();
    });
  }
  function runFlipbook() {
    var i = 0;
    function show() {
      flipImg.src = PITCH_IMG + FLIPBOOK[i];
      flipLabelEl.textContent = flipLabel(i);
      flipTimer = setTimeout(function () { i = nextFlip(i); show(); }, flipDelay(i));
    }
    show();
  }
  function preload() {
    FLIPBOOK.forEach(function (name) { var im = new Image(); im.src = PITCH_IMG + name; });
  }

  function onKey(e) {
    var t = e.target;
    if (t && t.matches && t.matches('input,textarea,select,[contenteditable]')) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    switch (e.key) {
      case 'ArrowRight': case ' ': case 'PageDown': e.preventDefault(); set(advance(state, deck)); return;
      case 'ArrowLeft': case 'PageUp': e.preventDefault(); set(back(state, deck)); return;
      case 'Home': set(jump(1, deck)); return;
      case 'End': set(jump(deck.cards, deck)); return;
      case 'f': case 'F': toggleFullscreen(); return;
      case '0': set(jump(10, deck)); return;
      default:
        if (/^[1-9]$/.test(e.key)) set(jump(parseInt(e.key, 10), deck));
    }
  }
  function onClick(e) {
    if (document.body.classList.contains('dev')) return;   // developer mode owns clicks
    if (e.target.closest && e.target.closest('a[href]')) return;   // links own their clicks
    var r = stage.getBoundingClientRect();
    var x = (e.clientX - r.left) / r.width;
    set(x < 1 / 3 ? back(state, deck) : advance(state, deck));
  }
  function toggleFullscreen() {
    if (document.fullscreenElement) { document.exitFullscreen(); return; }
    if (stage.requestFullscreen) stage.requestFullscreen();
    else if (stage.webkitRequestFullscreen) stage.webkitRequestFullscreen();
  }

  document.addEventListener('DOMContentLoaded', function () {
    stage = document.querySelector('.stage');
    setup(parseCut(location.search));
    counters = Array.prototype.slice.call(document.querySelectorAll('.counter'));
    flipImg = document.getElementById('flip');
    flipLabelEl = document.getElementById('flipLabel');
    flipCard = flipImg ? flipImg.closest('.card') : null;
    videos = Array.prototype.slice.call(document.querySelectorAll('video'));
    stage.classList.toggle('shownotes', parseNotes(location.search));
    state = { card: parseHash(location.hash, deck), build: 0 };
    document.addEventListener('keydown', onKey);
    stage.addEventListener('click', onClick);
    window.addEventListener('hashchange', function () {
      var card = parseHash(location.hash, deck);
      if (card !== state.card) set(jump(card, deck));
    });
    preload();
    render();
  });
})();
```

- [ ] **Step 4: Run the tests to see them pass**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: `# pass 9`, `# fail 0`.

- [ ] **Step 5: Commit**

```bash
git add docs/duet/class/class.js code/hackathon/pagetests/class.test.mjs
git commit -m "feat(class): deck navigation with a page-sized card count, ?cut=10, reveals, flipbook and clips tied to the shown card

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: The page shell, `class.css` base, and Act 1 (cards 1–4)

**Files:**
- Create: `docs/duet/class/index.html`
- Create: `docs/duet/class/class.css`
- Modify: `code/hackathon/pagetests/class.test.mjs` (append)

- [ ] **Step 1: Append the failing tests for the shell and Act 1**

Append to `code/hackathon/pagetests/class.test.mjs`:

```js
/* ---- the page ---- */
const sectionsOf = (h) => h.split(/<section class="card /).slice(1);
const specsFromHtml = (h) => [...h.matchAll(/<section class="card [^"]*" data-card="(\d+)"([^>]*)>/g)].map((m) => ({
  cut: (/data-cut="(\d+)"/.exec(m[2]) || [, ''])[1],
  builds: parseInt((/data-builds="(\d+)"/.exec(m[2]) || [, '0'])[1], 10),
}));

test('the page links the pitch\'s font, stylesheet and developer mode, then its own, as classic scripts', () => {
  const h = read('index.html');
  assert.match(h, /<title>A robot that draws back<\/title>/);
  for (const f of ['../pitch/fredoka.css', '../pitch/deck.css', 'class.css']) assert.ok(h.includes(`<link rel="stylesheet" href="${f}">`), `${f} linked`);
  assert.ok(h.includes('<script src="class.js"></script>') && h.includes('<script src="../pitch/dev.js"></script>'), 'scripts');
  assert.ok(!/type="module"/.test(h), 'module scripts do not load over file:// in Chrome');
  assert.ok(!h.includes('deck.js"'), 'the pitch\'s navigation is not loaded');
  for (const id of ['id="squiggle"', 'id="squiggle-bright"', 'id="logo"']) assert.ok(h.includes(id), `svg def ${id}`);
  assert.ok(!/[‘’]/.test(h), 'use plain apostrophes so quotes are searchable');
});

test('Act 1: the title, the hackathon, the other teams, the diner', () => {
  const h = read('index.html');
  const s = sectionsOf(h);
  assert.ok(s.length >= 4);
  const copy = [
    'A robot that draws <span class="key">back</span>.', 'Two days at a robot hackathon.',
    'Friday 9 am to Saturday 6 pm. Doors lock at night.', 'Teams of 2 or 3. A real robot arm each.', 'Demo at 3:30. Awards at 5.',
    'My dad was an architect. He always had a pen.',
    'At the diner, while we waited for the food, we\'d draw together.',
    'He\'d draw. I\'d draw on top. He\'d draw again. Until the food came.',
    'I didn\'t figure out that\'s where this came from until halfway through building it.',
  ];
  for (const line of copy) assert.ok(h.includes(line), `copy missing: ${line}`);
  assert.ok(s[0].includes('src="img/setup.jpg"'), 'card 1 hero is the arm photo');
  assert.ok(s[1].includes('src="img/door.jpg"') && s[1].includes('src="img/crowd.jpg"'), 'card 2 shows the door and the room');
  const videos = [...s[2].matchAll(/<video ([^>]*)>/g)].map((m) => m[1]);
  assert.equal(videos.length, 4, 'card 3 has four clips');
  videos.forEach((attrs, i) => {
    for (const a of ['muted', 'loop', 'playsinline', 'preload="auto"']) assert.ok(attrs.includes(a), `clip ${i + 1} ${a}`);
    assert.ok(!/\bautoplay\b/.test(attrs), `clip ${i + 1} has no autoplay: class.js plays it on its card`);
    assert.ok(attrs.includes(`src="video/team-${i + 1}.mp4"`), `clip ${i + 1} source`);
  });
  assert.ok(/class="card split lines plate-black"/.test('class="card ' + s[3].slice(0, 60)), 'card 4 is the black text card');
  assert.equal((s[3].match(/class="line reveal headline" data-step="(\d)"/g) || []).length, 4, 'card 4 reveals four lines');
  assert.ok(s[3].includes('data-builds="4"'), 'card 4 declares four reveals');
});

test('class.css: reveals, the half template, no stray font sizes, no redefinition of the pitch\'s tokens', () => {
  const css = read('class.css');
  assert.match(css, /\.reveal \{ opacity: 0;/);
  assert.match(css, /\.reveal\.shown \{ opacity: 1; transform: none; \}/);
  assert.match(css, /\.stage \.card\.active \.triptych \.module\.reveal \{ animation: none; \}/);
  assert.match(css, /\.split\.half \.words \{ grid-column: 1 \/ 7; \}/);
  assert.match(css, /\.split\.half\.photo-left \.figure \{ grid-column: 1 \/ 6; grid-row: 1; \}/);
  const sizes = [...css.matchAll(/font-size:\s*([^;}]+)/g)].map((m) => m[1].trim());
  for (const v of sizes) assert.match(v, /^var\(--(display|headline|body|caption)\)$/, `font-size "${v}" is not a token`);
  assert.ok(!/^:root \{[^}]*--(display|headline|body|caption):/m.test(css), 'the type scale stays in deck.css');
});
```

- [ ] **Step 2: Run the tests to see the new ones fail**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: the 9 from Task 2 pass; the 3 new ones fail with `ENOENT ... index.html` / `class.css`.

- [ ] **Step 3: Write `class.css`**

Create `docs/duet/class/class.css`:

```css
/* Duet class deck: only what deck.css lacks. The type scale, plates, master page, split/triptych/modules templates, paper,
   pills, bubble, flipbook, pop entrance and developer mode all come from ../pitch/deck.css. Every font-size here is a
   token; a size steps by redefining the token on the element, the pitch's rule. */
:root { --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace; }

/* reveals: elements with data-step appear one advance at a time; class.js sets .shown */
.reveal { opacity: 0; transform: translateY(1cqw); transition: opacity .4s ease, transform .4s ease; }
.reveal.shown { opacity: 1; transform: none; }
.stage .card.active .triptych .module.reveal { animation: none; }   /* the pop's fill mode would override the reveal */

/* template: half (words in cols 1-7, figure in cols 7-13); photo-left puts the figure first */
.split.half .words { grid-column: 1 / 7; }
.split.half .figure { grid-column: 7 / 13; display: flex; flex-direction: column; justify-content: center; align-items: center; gap: var(--s1); }
.split.half.photo-left .figure { grid-column: 1 / 6; grid-row: 1; }
.split.half.photo-left .words { grid-column: 6 / 13; grid-row: 1; }
.half .photo img { height: 33cqw; width: auto; max-width: 100%; }

/* the modules template's own children pop in deck.css; these are the class deck's */
.card.active .modules .content > :is(.duo, .facts, .clips, .codes, .flipwrap, .display, .takeaway) {
  animation: pop calc(.45s / var(--speed, 1)) cubic-bezier(.2, .7, .3, 1) both;
  animation-delay: calc(var(--i, 3) * var(--stagger, 80ms) / var(--speed, 1)); }

/* takeaways: the lesson of a card, a yellow paper line set apart */
.takeaway { background: var(--yellow); align-self: flex-start; }

/* card 1: title */
.title .display { --display: 7cqw; }

/* card 2: two photos and three facts */
.duo { display: grid; grid-template-columns: 1fr 1fr; column-gap: var(--gutter); }
.duo .photo img { height: 22cqw; width: 100%; object-fit: cover; }
.facts { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); column-gap: var(--gutter); }
.facts .paper { --body: 2.4cqw; text-align: center; }

/* card 3: four portrait clips in a row */
.clips { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); column-gap: var(--gutter); }
.clip { display: flex; flex-direction: column; align-items: center; gap: .6cqw; min-width: 0; }
.clip video { display: block; height: 30cqw; width: 100%; object-fit: cover; border-radius: calc(var(--paper-radius) - .4cqw); background: #000; }
.clip .cap { --body: 2.2cqw; min-height: 1.3em; }

/* card 4: four lines on the black plate */
.lines .words { grid-column: 1 / 13; gap: var(--s2); }
.lines .line { --headline: 4.6cqw; }

/* card 5: the setup with numbered callouts on the photo */
.callouts .words { gap: var(--s1); }
.callouts .headline { --headline: 4.4cqw; }
.callouts .list { display: flex; flex-direction: column; gap: var(--s1); }
.callouts .list .paper { --body: 2.5cqw; padding: .8cqw var(--paper-pad); }
.shot { position: relative; width: fit-content; }
.dot { position: absolute; left: var(--x); top: var(--y); width: 4cqw; height: 4cqw; border-radius: 50%; background: var(--yellow); color: var(--ink);
       border: var(--paper-border) solid var(--ink); display: flex; align-items: center; justify-content: center;
       font-size: var(--body); font-weight: 700; box-shadow: .3cqw .3cqw 0 var(--ink); }
.dot.reveal { transform: translate(-50%, -50%) scale(.6); }
.dot.reveal.shown { transform: translate(-50%, -50%) scale(1); }

/* card 6: a verb over each module of the triptych */
.oneturn .verb { --display: 6cqw; letter-spacing: .08em; color: #fff; -webkit-text-stroke: .04em var(--ink); paint-order: stroke fill; }
.oneturn .photo img { height: 22cqw; }
.oneturn .m2 .bubble { --body: 2.4cqw; }
.oneturn .cap { --body: 2.2cqw; }

/* card 7: two code panels */
.code .headline { --headline: 3.8cqw; }
.codes { display: grid; grid-template-columns: 1fr 1fr; column-gap: var(--s2); }
.codepanel { display: flex; flex-direction: column; gap: .6cqw; }
.codepanel pre { margin: 0; font-family: var(--mono); --body: 1.7cqw; font-size: var(--body); font-weight: 500; line-height: 1.35; white-space: pre; overflow: hidden; }

/* card 8: the flipbook, a line under it */
.watch .flip img { height: 25cqw; }
.watch .closing { text-align: center; color: #fff; }

/* card 9: the big number */
.big .content { align-items: center; text-align: center; }
.big .display { --display: 12cqw; line-height: 1; }
.big .closing { --body: 2.6cqw; }
.big .takeaway { align-self: center; }

/* card 10: the Go button */
.gobtn { display: inline-block; padding: var(--s2) var(--s4); background: var(--green); color: #fff; border: var(--paper-border) solid var(--ink);
         border-radius: 999px; font-size: var(--headline); font-weight: 700; line-height: 1; box-shadow: .7cqw .7cqw 0 var(--ink); }
.trigger .words { gap: var(--s1); }
.trigger .headline { --headline: 4.6cqw; }
.trigger .words .body { --body: 2.4cqw; }

/* card 11: the excerpt and the error line */
.error .figure { align-items: stretch; }
.errline { color: var(--human); font-family: var(--mono); }

/* card 12: the four log fields */
.logfields .paper { display: flex; flex-direction: column; gap: .4cqw; align-items: flex-start; }
.logfields .num { --display: 6cqw; line-height: 1; color: var(--blue); }

/* card 13: three lines beside the medal */
.felt .words { gap: var(--s1); }

/* card 14: the advice, two lines on the black plate */
.advice .words { grid-column: 1 / 13; gap: var(--s3); }
```

- [ ] **Step 4: Write `index.html` with the shell and cards 1–4**

Create `docs/duet/class/index.html`. The `<svg class="defs">` block is the pitch's, minus the artist chips and step icons this deck does not use.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>A robot that draws back</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E%3Crect width=%2732%27 height=%2732%27 rx=%276%27 fill=%27%23ffd400%27/%3E%3Cpath d=%27M6 20q5-9 10 0t10 0%27 fill=%27none%27 stroke=%27%23111%27 stroke-width=%274%27 stroke-linecap=%27round%27/%3E%3C/svg%3E">
<link rel="stylesheet" href="../pitch/fredoka.css">
<link rel="stylesheet" href="../pitch/deck.css">
<link rel="stylesheet" href="class.css">
</head>
<body>

<svg class="defs" aria-hidden="true" focusable="false">
  <defs>
    <!-- squiggle motifs on a 160 x 160 tile, from the pitch deck -->
    <path id="m-wave" d="M0 24 q10 -14 20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0"/>
    <path id="m-zig" d="M0 140 l10 -14 l10 14 l10 -14 l10 14 l10 -14 l10 14 l10 -14 l10 14 l10 -14 l10 14 l10 -14 l10 14 l10 -14 l10 14 l10 -14 l10 14"/>
    <path id="m-ticks" d="M96 56 l-10 -10 M110 50 l0 -14 M124 56 l10 -10 M90 70 l-14 0 M130 70 l14 0"/>
    <path id="m-dots" d="M30 70 l.01 0 M50 100 l.01 0" stroke-width="10"/>
    <path id="m-arcs" d="M14 56 a18 18 0 0 1 36 0 M60 116 a14 14 0 0 0 28 0"/>
    <pattern id="squiggle" width="160" height="160" patternUnits="userSpaceOnUse">
      <g fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
        <use href="#m-wave"/><use href="#m-zig"/><use href="#m-ticks"/><use href="#m-dots"/><use href="#m-arcs"/>
      </g>
    </pattern>
    <pattern id="squiggle-bright" width="160" height="160" patternUnits="userSpaceOnUse">
      <g fill="none" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
        <use href="#m-wave" stroke="#ffd400"/><use href="#m-zig" stroke="#e5322d"/><use href="#m-ticks" stroke="#1f4fd6"/>
        <use href="#m-dots" stroke="#17a34a"/><use href="#m-arcs" stroke="#ff7a00"/>
      </g>
    </pattern>
    <!-- the Duet logo: four toy alphabet blocks and a marker squiggle; ink parts in currentColor -->
    <symbol id="logo" viewBox="0 0 320 130">
      <g transform="rotate(-6 52 64)"><rect x="20" y="32" width="64" height="64" rx="12" fill="#ffd400" stroke="currentColor" stroke-width="5"/><text x="52" y="66" font-family="Fredoka, 'Chalkboard SE', sans-serif" font-weight="700" font-size="46" text-anchor="middle" dominant-baseline="central" fill="currentColor">D</text></g>
      <g transform="rotate(4 124 64)"><rect x="92" y="32" width="64" height="64" rx="12" fill="#e5322d" stroke="currentColor" stroke-width="5"/><text x="124" y="66" font-family="Fredoka, 'Chalkboard SE', sans-serif" font-weight="700" font-size="46" text-anchor="middle" dominant-baseline="central" fill="currentColor">U</text></g>
      <g transform="rotate(-3 196 64)"><rect x="164" y="32" width="64" height="64" rx="12" fill="#1f4fd6" stroke="currentColor" stroke-width="5"/><text x="196" y="66" font-family="Fredoka, 'Chalkboard SE', sans-serif" font-weight="700" font-size="46" text-anchor="middle" dominant-baseline="central" fill="currentColor">E</text></g>
      <g transform="rotate(5 268 64)"><rect x="236" y="32" width="64" height="64" rx="12" fill="#17a34a" stroke="currentColor" stroke-width="5"/><text x="268" y="66" font-family="Fredoka, 'Chalkboard SE', sans-serif" font-weight="700" font-size="46" text-anchor="middle" dominant-baseline="central" fill="currentColor">T</text></g>
      <path d="M40 118 q10 -10 20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round"/>
    </symbol>
  </defs>
</svg>

<div class="stage" data-el="stage">

  <section class="card split half title plate-yellow" data-card="1" data-el="card 1 — title">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="../pitch/img/plate-1.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="wash" aria-hidden="true"></div>
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 1 kicker">01 · Duet</span><span class="wordmark" data-el="card 1 wordmark"><svg class="logo" viewBox="0 0 320 130" role="img" aria-label="Duet"><use href="#logo"/></svg></span></header>
    <div class="content">
      <div class="words">
        <h1 class="display" data-el="card 1 headline">A robot that draws <span class="key">back</span>.</h1>
        <p class="body" data-el="card 1 subtitle">Two days at a robot hackathon.</p>
      </div>
      <figure class="paper photo figure" data-el="card 1 photo — the arm over the board"><img src="img/setup.jpg" alt="A robot arm holding a green marker over a whiteboard, a laptop beside it"></figure>
    </div>
    <aside class="notes" data-el="card 1 notes — the spoken part"><p>Hi, I'm Nicholas. Last weekend I spent two days at a robot hackathon in New York and built this: a robot arm that draws with you. I'll show you what it is, how it works, and everything that went wrong on the way. Ask in the chat whenever you want; I can see it.</p></aside>
    <footer class="band foot"><span class="strip" data-el="card 1 footer">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026</span><span class="counter">1 / 14</span></footer>
  </section>

  <section class="card modules hackathon plate-red" data-card="2" data-el="card 2 — what a hackathon is">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="../pitch/img/plate-2.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="wash" aria-hidden="true"></div>
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 2 kicker">02 · What a hackathon is</span><span class="wordmark" data-el="card 2 wordmark"><svg class="logo" viewBox="0 0 320 130" role="img" aria-label="Duet"><use href="#logo"/></svg></span></header>
    <div class="content">
      <div class="duo">
        <figure class="paper photo" data-el="card 2 photo — the door sign"><img src="img/door.jpg" alt="A green sign on a glass door: Please, check in before hacking"></figure>
        <figure class="paper photo" data-el="card 2 photo — demo day"><img src="img/crowd.jpg" alt="A crowd around a robot arm on demo day"></figure>
      </div>
      <ul class="facts">
        <li class="paper body" data-el="card 2 fact — hours">Friday 9 am to Saturday 6 pm. Doors lock at night.</li>
        <li class="paper body" data-el="card 2 fact — teams">Teams of 2 or 3. A real robot arm each.</li>
        <li class="paper body" data-el="card 2 fact — demo">Demo at 3:30. Awards at 5.</li>
      </ul>
    </div>
    <aside class="notes" data-el="card 2 notes — the spoken part"><p>A hackathon is a weekend where people show up to a room with a problem and try to build something real before the time runs out. Viam, a company that makes software for robots, lent every team a real arm. The theme was fine motor skills: plug in a charger, pour water, stack Jenga, sort recycling, move an egg. Or bring your own idea. I brought my own.</p></aside>
    <footer class="band foot"><span class="strip" data-el="card 2 footer">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026</span><span class="counter">2 / 14</span></footer>
  </section>

  <section class="card modules teams plate-blue" data-card="3" data-cut="20" data-el="card 3 — what other teams built">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="../pitch/img/plate-3.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="wash" aria-hidden="true"></div>
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 3 kicker">03 · What other teams built</span><span class="wordmark" data-el="card 3 wordmark"><svg class="logo" viewBox="0 0 320 130" role="img" aria-label="Duet"><use href="#logo"/></svg></span></header>
    <div class="content">
      <div class="clips">
        <div class="clip paper" data-el="card 3 clip — team 1"><video src="video/team-1.mp4" muted loop playsinline preload="auto"></video><p class="cap body" data-el="card 3 caption — team 1"></p></div>
        <div class="clip paper" data-el="card 3 clip — team 2"><video src="video/team-2.mp4" muted loop playsinline preload="auto"></video><p class="cap body" data-el="card 3 caption — team 2"></p></div>
        <div class="clip paper" data-el="card 3 clip — team 3"><video src="video/team-3.mp4" muted loop playsinline preload="auto"></video><p class="cap body" data-el="card 3 caption — team 3"></p></div>
        <div class="clip paper" data-el="card 3 clip — team 4"><video src="video/team-4.mp4" muted loop playsinline preload="auto"></video><p class="cap body" data-el="card 3 caption — team 4"></p></div>
      </div>
    </div>
    <aside class="notes" data-el="card 3 notes — the spoken part"><p>Four other teams, same arm, same two days. One line about each. Every one of these started with someone saying: what if it could.</p></aside>
    <footer class="band foot"><span class="strip" data-el="card 3 footer">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026</span><span class="counter">3 / 14</span></footer>
  </section>

  <section class="card split lines plate-black" data-card="4" data-builds="4" data-el="card 4 — why I built this">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle-bright)"/></svg>
    <img class="plate-img" src="../pitch/img/plate-7.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="wash" aria-hidden="true"></div>
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 4 kicker">04 · Why I built this</span><span class="wordmark" data-el="card 4 wordmark"><svg class="logo" viewBox="0 0 320 130" role="img" aria-label="Duet"><use href="#logo"/></svg></span></header>
    <div class="content">
      <div class="words">
        <p class="line reveal headline" data-step="1" data-el="card 4 line 1">My dad was an architect. He always had a pen.</p>
        <p class="line reveal headline" data-step="2" data-el="card 4 line 2">At the diner, while we waited for the food, we'd draw together.</p>
        <p class="line reveal headline" data-step="3" data-el="card 4 line 3">He'd draw. I'd draw on top. He'd draw again. Until the food came.</p>
        <p class="line reveal headline" data-step="4" data-el="card 4 line 4">I didn't figure out that's where this came from until halfway through building it.</p>
      </div>
    </div>
    <aside class="notes" data-el="card 4 notes — the spoken part"><p>Why a robot that draws with you. My dad was an architect; he always had a pen. At the diner we'd draw together on the placemat until the food came. That's how I got into art. I walked into the hackathon thinking it would be fun to sketch with a robot, and only halfway through building it did I realize I'd built the other side of that table.</p></aside>
    <footer class="band foot"><span class="strip" data-el="card 4 footer">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026</span><span class="counter">4 / 14</span></footer>
  </section>

</div>

<div class="dev-badge">DEV MODE &middot; click an element to copy its name &middot; press D to exit</div>
<div class="dev-label" id="devLabel"></div>
<div class="dev-toast" id="devToast"></div>

<script src="class.js"></script>
<script src="../pitch/dev.js"></script>
</body>
</html>
```

- [ ] **Step 5: Run the tests to see them pass**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: `# pass 12`, `# fail 0`.

- [ ] **Step 6: Look at it in the browser**

Create `.claude/launch.json` in the worktree (untracked; do not commit):

```json
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "class",
      "runtimeExecutable": "python3",
      "runtimeArgs": ["-m", "http.server", "8792", "--directory", "docs/duet"],
      "port": 8792
    }
  ]
}
```

Open the `class` preview and navigate to `http://localhost:8792/class/index.html`. Check: card 1 shows the arm photo beside the title; Right arrow moves to card 2 (two photos, three facts), card 3 (four clips playing), card 4 (black; four presses reveal four lines; a fifth press does nothing yet, since card 5 does not exist). Console: no errors other than 404s for cards not yet built. Fix any overflow (a card's content spilling past the frame) by stepping the token on that card's block in `class.css`, never by writing a font size.

- [ ] **Step 7: Commit**

```bash
git add docs/duet/class/index.html docs/duet/class/class.css code/hackathon/pagetests/class.test.mjs
git commit -m "feat(class): page shell and Act 1, the room: title, hackathon, other teams, the diner

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: Act 2 — the machine (cards 5–8)

**Files:**
- Modify: `docs/duet/class/index.html` (insert after card 4's `</section>`)
- Modify: `code/hackathon/pagetests/class.test.mjs` (append)

- [ ] **Step 1: Append the failing tests for Act 2**

```js
test('Act 2: the setup with callouts, one turn with three verbs, the two code panels, the flipbook', () => {
  const h = read('index.html');
  const s = sectionsOf(h);
  assert.ok(s.length >= 8);
  const copy = [
    'You draw. It looks. It thinks. It draws back.',
    '1 · a camera on the wrist', '2 · a gripper holding a green marker', '3 · the board: red is a person, green is the robot', '4 · the laptop running the code',
    '>LOOK<', '>THINK<', '>DRAW<', 'the camera takes a photo', 'the arm follows the points',
    'A crowded world of creatures, flowers and dancing figures.',
    'A small green dancing figure in the open lower-right space to balance the crowd.',
    '8 seconds to look and decide', 'Claude says',
    'Your turtle and my robot follow the same thing: a list of points.', 'Your turtle', 'My robot (simplified)',
    'Play with it after: viam-duet.vercel.app',
  ];
  for (const line of copy) assert.ok(h.includes(line), `copy missing: ${line}`);
  // card 5: a photo-left half card, four dots on the photo and four list items, all reveals 1..4
  assert.ok(/^split half photo-left callouts /.test(s[4]), 'card 5 template');
  assert.ok(s[4].includes('data-builds="4"'));
  assert.deepEqual([...s[4].matchAll(/class="dot reveal" data-step="(\d)"/g)].map((m) => m[1]), ['1', '2', '3', '4']);
  assert.deepEqual([...s[4].matchAll(/class="paper body line reveal" data-step="(\d)"/g)].map((m) => m[1]), ['1', '2', '3', '4']);
  assert.ok(s[4].includes('src="img/setup.jpg"'));
  // card 6: the pitch's triptych, each module a reveal with its verb
  assert.ok(/^triptych oneturn /.test(s[5]), 'card 6 template');
  assert.ok(s[5].includes('data-builds="3"'));
  assert.deepEqual([...s[5].matchAll(/class="module m\d reveal" data-step="(\d)"/g)].map((m) => m[1]), ['1', '2', '3']);
  assert.ok(s[5].includes('src="../pitch/img/turn-07-human.jpg"') && s[5].includes('src="../pitch/img/turn-07-robot.jpg"'), 'card 6 uses the crowded-world turn');
  assert.match(s[5], /<div class="paper bubble body"[^>]*>\s*<span class="caption says"/, 'card 6 names the speaker at the top of its bubble');
  // card 7: two <pre> panels, verbatim
  const turtle = [
    'import turtle', 't = turtle.Turtle()', 'points = [(40, 0), (40, 40),', '          (0, 40), (0, 0)]',
    't.penup()', 't.goto(0, 0)', 't.pendown()', 'for x, y in points:', '    t.goto(x, y)', 't.penup()',
  ].join('\n');
  const robot = [
    'stroke = points_from_claude()', '# e.g. [(0, 0), (40, 0), (40, 40)]', 'x, y = stroke[0]',
    'pen_up()', 'move_to(x, y)', 'pen_down()', 'for x, y in stroke[1:]:', '    move_to(x, y)', 'pen_up()',
  ].join('\n');
  assert.ok(s[6].includes(`<pre>${turtle}</pre>`), 'turtle panel verbatim');
  assert.ok(s[6].includes(`<pre>${robot}</pre>`), 'robot panel verbatim');
  assert.equal((s[6].match(/<pre>/g) || []).length, 2);
  // card 8: the flipbook elements the wiring looks for
  assert.ok(s[7].includes('id="flip"') && s[7].includes('id="flipLabel"'), 'card 8 flipbook');
  assert.ok(s[7].includes('src="../pitch/img/turn-00-start.jpg"'), 'the flipbook starts on the blank board');
});
```

- [ ] **Step 2: Run the tests to see the new one fail**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: 12 pass, 1 fails (`copy missing: You draw. It looks...`).

- [ ] **Step 3: Insert cards 5–8 after card 4's `</section>`**

```html
  <section class="card split half photo-left callouts plate-orange" data-card="5" data-builds="4" data-el="card 5 — what Duet is">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="../pitch/img/plate-5.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="wash" aria-hidden="true"></div>
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 5 kicker">05 · What Duet is</span><span class="wordmark" data-el="card 5 wordmark"><svg class="logo" viewBox="0 0 320 130" role="img" aria-label="Duet"><use href="#logo"/></svg></span></header>
    <div class="content">
      <figure class="paper photo figure" data-el="card 5 photo — the setup">
        <div class="shot">
          <img src="img/setup.jpg" alt="The arm over the board: camera on the wrist, gripper holding a green marker, the board, the laptop">
          <span class="dot reveal" data-step="1" style="--x: 44%; --y: 19%" data-el="card 5 dot — 1 camera">1</span>
          <span class="dot reveal" data-step="2" style="--x: 43%; --y: 30%" data-el="card 5 dot — 2 gripper">2</span>
          <span class="dot reveal" data-step="3" style="--x: 52%; --y: 51%" data-el="card 5 dot — 3 board">3</span>
          <span class="dot reveal" data-step="4" style="--x: 72%; --y: 72%" data-el="card 5 dot — 4 laptop">4</span>
        </div>
      </figure>
      <div class="words">
        <h2 class="headline" data-el="card 5 headline">You draw. It looks. It thinks. It draws back.</h2>
        <ul class="list">
          <li class="paper body line reveal" data-step="1" data-el="card 5 callout — 1 camera">1 · a camera on the wrist</li>
          <li class="paper body line reveal" data-step="2" data-el="card 5 callout — 2 gripper">2 · a gripper holding a green marker</li>
          <li class="paper body line reveal" data-step="3" data-el="card 5 callout — 3 board">3 · the board: red is a person, green is the robot</li>
          <li class="paper body line reveal" data-step="4" data-el="card 5 callout — 4 laptop">4 · the laptop running the code</li>
        </ul>
      </div>
    </div>
    <aside class="notes" data-el="card 5 notes — the spoken part"><p>The setup. On the arm's wrist, a camera. Below it, the gripper, holding a green marker. On the table, the board: red lines are a person's, green lines are the robot's. And my laptop, running the code. That's all of it.</p></aside>
    <footer class="band foot"><span class="strip" data-el="card 5 footer">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026</span><span class="counter">5 / 14</span></footer>
  </section>

  <section class="card triptych oneturn plate-cream" data-card="6" data-builds="3" data-el="card 6 — one turn">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="../pitch/img/plate-6.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="wash" aria-hidden="true"></div>
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 6 kicker">06 · One turn</span><span class="wordmark" data-el="card 6 wordmark"><svg class="logo" viewBox="0 0 320 130" role="img" aria-label="Duet"><use href="#logo"/></svg></span></header>
    <div class="content">
      <div class="module m1 reveal" data-step="1" data-el="card 6 module — LOOK">
        <span class="verb display" data-el="card 6 verb — LOOK">LOOK</span>
        <figure class="paper photo" data-el="card 6 photo — the person's mark"><img src="../pitch/img/turn-07-human.jpg" alt="The board after the person's turn"></figure>
        <p class="cap body" data-el="card 6 caption — LOOK">the camera takes a photo</p>
      </div>
      <div class="module m2 reveal" data-step="2" data-el="card 6 module — THINK">
        <span class="verb display" data-el="card 6 verb — THINK">THINK</span>
        <div class="paper bubble body" data-el="card 6 speech bubble">
          <span class="caption says" data-el="card 6 speech bubble — who">Claude says</span>
          <p class="sees" data-el="card 6 speech bubble — sees">A crowded world of creatures, flowers and dancing figures.</p>
          <p class="adds" data-el="card 6 speech bubble — adds">A small green dancing figure in the open lower-right space to balance the crowd.</p>
          <span class="pill" data-el="card 6 badge — latency">8 seconds to look and decide</span>
        </div>
      </div>
      <div class="module m3 reveal" data-step="3" data-el="card 6 module — DRAW">
        <span class="verb display" data-el="card 6 verb — DRAW">DRAW</span>
        <figure class="paper photo" data-el="card 6 photo — the robot's answer"><img src="../pitch/img/turn-07-robot.jpg" alt="The board after the robot's green figure"></figure>
        <p class="cap body" data-el="card 6 caption — DRAW">the arm follows the points</p>
      </div>
    </div>
    <aside class="notes" data-el="card 6 notes — the spoken part"><p>Look: you draw and press Go; the camera takes a photo. Think: the photo goes to Claude, an AI that can look at a picture and tell you what's in it. I ask what it sees and what it would add. This answer is real, from the hackathon, about eight seconds. Draw: Claude also sends the shape as a list of points, and the arm follows them.</p></aside>
    <footer class="band foot"><span class="strip" data-el="card 6 footer">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026</span><span class="counter">6 / 14</span></footer>
  </section>

  <section class="card modules code plate-black" data-card="7" data-el="card 7 — it's just points">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle-bright)"/></svg>
    <img class="plate-img" src="../pitch/img/plate-7.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="wash" aria-hidden="true"></div>
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 7 kicker">07 · It's just points</span><span class="wordmark" data-el="card 7 wordmark"><svg class="logo" viewBox="0 0 320 130" role="img" aria-label="Duet"><use href="#logo"/></svg></span></header>
    <div class="content">
      <div class="lead"><h2 class="headline" data-el="card 7 headline">Your turtle and my robot follow the same thing: a list of points.</h2></div>
      <div class="codes">
        <div class="paper codepanel" data-el="card 7 code — your turtle"><span class="caption" data-el="card 7 code label — your turtle">Your turtle</span><pre>import turtle
t = turtle.Turtle()
points = [(40, 0), (40, 40),
          (0, 40), (0, 0)]
t.penup()
t.goto(0, 0)
t.pendown()
for x, y in points:
    t.goto(x, y)
t.penup()</pre></div>
        <div class="paper codepanel" data-el="card 7 code — my robot"><span class="caption" data-el="card 7 code label — my robot">My robot (simplified)</span><pre>stroke = points_from_claude()
# e.g. [(0, 0), (40, 0), (40, 40)]
x, y = stroke[0]
pen_up()
move_to(x, y)
pen_down()
for x, y in stroke[1:]:
    move_to(x, y)
pen_up()</pre></div>
      </div>
    </div>
    <aside class="notes" data-el="card 7 notes — the spoken part"><p>Left is turtle: pen up, go to the start, pen down, go through a list of points, pen up. Right is my robot, simplified: pen up, move to the start, pen down, go through a list of points, pen up. Same program. Mine has a motor.</p></aside>
    <footer class="band foot"><span class="strip" data-el="card 7 footer">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026</span><span class="counter">7 / 14</span></footer>
  </section>

  <section class="card modules watch plate-yellow" data-card="8" data-el="card 8 — watch it">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="../pitch/img/plate-1.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="wash" aria-hidden="true"></div>
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 8 kicker">08 · Watch it</span><span class="wordmark" data-el="card 8 wordmark"><svg class="logo" viewBox="0 0 320 130" role="img" aria-label="Duet"><use href="#logo"/></svg></span></header>
    <div class="content">
      <div class="flipwrap">
        <figure class="paper photo flip" data-el="card 8 flipbook image"><img id="flip" src="../pitch/img/turn-00-start.jpg" alt="The board, turn by turn"></figure>
        <span class="pill" id="flipLabel" data-el="card 8 flipbook counter">start</span>
      </div>
      <p class="closing body" data-el="card 8 closing">Play with it after: viam-duet.vercel.app</p>
    </div>
    <aside class="notes" data-el="card 8 notes — the spoken part"><p>A whole session. Ten turns. Red is the person, green is the robot. Every green line is the robot answering a red one. The web version replays a real session with what Claude said at every turn; play with it after class.</p></aside>
    <footer class="band foot"><span class="strip" data-el="card 8 footer">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026</span><span class="counter">8 / 14</span></footer>
  </section>
```

- [ ] **Step 4: Run the tests to see them pass**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: `# pass 13`, `# fail 0`.

- [ ] **Step 5: Check cards 5–8 in the browser**

Reload `http://localhost:8792/class/index.html#5`. Card 5: the photo left, headline right, four advances reveal a numbered dot on the photo and its line on the right together; check each dot sits on the thing it names (camera box on the wrist, gripper and marker, the board, the laptop screen) and nudge the `--x`/`--y` percentages in the HTML if not. Card 6: three advances reveal LOOK, THINK, DRAW left to right; the bubble tail points at the DRAW module. Card 7: both panels fully visible, no clipped lines; if a line clips, step `.codepanel pre { --body: 1.7cqw }` down to `1.6cqw`. Card 8: the flipbook cycles with its label; leave the card and come back and it restarts; open the console and confirm no errors.

- [ ] **Step 6: Commit**

```bash
git add docs/duet/class/index.html code/hackathon/pagetests/class.test.mjs
git commit -m "feat(class): Act 2, the machine: the setup with callouts, one turn, it's just points, the flipbook

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Act 3 — what broke (cards 9–14), and the whole-deck structural tests

**Files:**
- Modify: `docs/duet/class/index.html` (insert after card 8's `</section>`)
- Modify: `code/hackathon/pagetests/class.test.mjs` (append)

- [ ] **Step 1: Append the failing tests for Act 3 and the whole deck**

```js
test('Act 3: three failures, the log, what it felt like, the advice', () => {
  const h = read('index.html');
  const s = sectionsOf(h);
  assert.equal(s.length, 14);
  const copy = [
    '27 mm', 'The robot crushed the pen.', 'I measured the board with the marker in my hand. The robot holds it 27 mm differently.', 'Measure with the robot\'s hand, not yours.',
    'The smart trigger that wasn\'t.', 'I wrote clever code so the robot would notice when you\'d stepped back.', 'It fired every few seconds on an empty board.',
    'Saturday morning I deleted it and added a button.', 'Go, robot!', 'The simple thing is allowed to win.',
    'The error you\'ll get too.', 'SyntaxError: \'return\' outside function', 'Four spaces instead of eight. The day before the hackathon.', 'The error message is the clue, not the insult.',
    'I wrote down every problem.', '>Symptom<', '>What I tried<', '>Fix<', '>Why it worked<', 'Nine entries in two days.', 'This is what debugging actually is.',
    'One person.', 'Two days.', '<span class="key">Honorable mention.</span>',
    'You already know <span class="key">enough</span> to start.', 'Start with the smallest thing that works, then make it bigger.',
  ];
  for (const line of copy) assert.ok(h.includes(line), `copy missing: ${line}`);
  const excerpt = ['class Palletizer:', '    def obstacles(self):', '        boxes = self.placed_boxes()', '    return WorldState(boxes)'].join('\n');
  assert.ok(s[10].includes(`<pre>${excerpt}</pre>`), 'card 11 excerpt verbatim');
  assert.ok(s[12].includes('src="img/medal.jpg"'), 'card 13 shows the medal');
  assert.ok(s[13].includes('data-builds="2"'), 'card 14 reveals two lines');
  assert.deepEqual([...s[13].matchAll(/class="line reveal headline" data-step="(\d)"/g)].map((m) => m[1]), ['1', '2']);
});

test('the page declares the cut and the reveals exactly as the tests model them, in order', () => {
  const h = read('index.html');
  assert.deepEqual(specsFromHtml(h), SPECS);
  const numbers = [...h.matchAll(/<section class="card [^"]*" data-card="(\d+)"/g)].map((m) => Number(m[1]));
  assert.deepEqual(numbers, Array.from({ length: 14 }, (_, i) => i + 1));
});

test('every card carries the master page: frame, wash, kicker, wordmark, footer with a counter, one notes aside', () => {
  const h = read('index.html');
  const kickers = ['01 · Duet', '02 · What a hackathon is', '03 · What other teams built', '04 · Why I built this', '05 · What Duet is', '06 · One turn',
    '07 · It\'s just points', '08 · Watch it', '09 · What broke', '10 · What broke', '11 · What broke', '12 · The log', '13 · What it felt like', '14 · One piece of advice'];
  const s = sectionsOf(h);
  assert.equal(s.length, 14);
  s.forEach((c, i) => {
    const n = i + 1;
    assert.ok(c.includes('class="kicker"') && c.includes(`>${kickers[i]}<`), `card ${n} kicker "${kickers[i]}"`);
    assert.equal((c.match(/class="wordmark"/g) || []).length, 1, `card ${n} has one wordmark`);
    assert.ok(/class="wordmark"[^>]*>\s*<svg class="logo/.test(c), `card ${n} header logo`);
    assert.ok(/class="band foot"/.test(c) && c.includes(`<span class="counter">${n} / 14</span>`), `card ${n} footer counter`);
    assert.ok(c.includes('Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026'), `card ${n} footer strip`);
    assert.ok(/class="frame"/.test(c) && c.includes('class="wash"') && c.includes('class="pattern"') && c.includes('class="plate-img"'), `card ${n} plate layers`);
    assert.ok(/^(split|triptych|modules) /.test(c), `card ${n} uses a pitch template class`);
    assert.equal((c.match(/<aside class="notes"/g) || []).length, 1, `card ${n} has one notes aside`);
    assert.ok(c.includes(`data-el="card ${n} notes — the spoken part"`), `card ${n} notes are named`);
    assert.ok(c.indexOf('<aside class="notes"') < c.indexOf('<footer class="band foot"'), `card ${n} notes sit above the footer`);
  });
  // plates cycle 1..7 with card 4 on black
  const plates = s.map((c) => /plate-(\d)\.jpg/.exec(c)[1]);
  assert.deepEqual(plates, ['1', '2', '3', '7', '5', '6', '7', '1', '2', '3', '4', '5', '6', '7']);
  assert.ok(/^split lines plate-black/.test(s[3]) && /^modules code plate-black/.test(s[6]) && /^split advice plate-black/.test(s[13]), 'cards 4, 7 and 14 are black');
});

test('developer mode is wired: badge, label, toast, and unique data-el names on every card', () => {
  const h = read('index.html');
  for (const x of ['class="dev-badge"', 'id="devLabel"', 'id="devToast"']) assert.ok(h.includes(x), x);
  const names = [...h.matchAll(/data-el="([^"]+)"/g)].map((m) => m[1]);
  assert.ok(names.length >= 90, `only ${names.length} data-el names`);
  assert.equal(new Set(names).size, names.length, 'data-el names must be unique');
  for (let n = 1; n <= 14; n++) assert.ok(names.some((x) => x.startsWith(`card ${n} `)), `card ${n} has no data-el`);
});

test('every local file the deck references exists, except the local-only assets, which are gitignored instead', () => {
  const h = read('index.html');
  const refs = [...h.matchAll(/(?:src|href)="([^"#:]+)"/g)].map((m) => m[1]);
  const localOnly = ['video/team-1.mp4', 'video/team-2.mp4', 'video/team-3.mp4', 'video/team-4.mp4', 'img/crowd.jpg', 'img/medal.jpg'];
  const ignore = readFileSync(ROOT + '.gitignore', 'utf8').split('\n');
  for (const r of new Set(refs)) {
    if (localOnly.includes(r)) {
      const rule = r.startsWith('video/') ? 'docs/duet/class/video/' : 'docs/duet/class/' + r;
      assert.ok(ignore.includes(rule), `${r} is local-only and must be gitignored as ${rule}`);
      continue;
    }
    assert.ok(existsSync(DIR + r), `referenced but missing: ${r}`);
  }
  for (const r of localOnly) assert.ok(refs.includes(r), `${r} is referenced`);
  assert.ok(refs.includes('img/setup.jpg') && refs.includes('img/door.jpg'), 'the two committed photos');
  assert.equal(refs.filter((r) => r.startsWith('../pitch/img/plate-')).length, 14, 'every card has a plate');
  assert.ok(ignore.includes('hackathon-videos/'), 'the source drop folder is gitignored');
});

test('the pitch deck is untouched by this work', () => {
  const pitch = fileURLToPath(new URL('../../../docs/duet/pitch/', import.meta.url));
  const js = readFileSync(pitch + 'deck.js', 'utf8');
  assert.match(js, /var CARDS = 7;/);
  assert.ok(!/ClassDeck/.test(js));
});
```

- [ ] **Step 2: Run the tests to see the new ones fail**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: 13 pass; the Act 3, cut/reveals, master-page, dev-mode and file-refs tests fail (`s.length` is 8); the pitch-untouched test passes.

- [ ] **Step 3: Insert cards 9–14 after card 8's `</section>`**

```html
  <section class="card modules big plate-red" data-card="9" data-cut="20" data-el="card 9 — the robot crushed the pen">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="../pitch/img/plate-2.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="wash" aria-hidden="true"></div>
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 9 kicker">09 · What broke</span><span class="wordmark" data-el="card 9 wordmark"><svg class="logo" viewBox="0 0 320 130" role="img" aria-label="Duet"><use href="#logo"/></svg></span></header>
    <div class="content">
      <p class="display key" data-el="card 9 number">27 mm</p>
      <div class="lead"><h2 class="headline" data-el="card 9 headline">The robot crushed the pen.</h2></div>
      <p class="closing body" data-el="card 9 line">I measured the board with the marker in my hand. The robot holds it 27 mm differently.</p>
      <p class="paper body takeaway" data-el="card 9 takeaway">Measure with the robot's hand, not yours.</p>
    </div>
    <aside class="notes" data-el="card 9 notes — the spoken part"><p>The first line it ever drew, it pushed so hard it flattened the marker tip. I had touched the marker to the corners of the board with the marker in my hand; the robot holds it 27 millimetres differently, more than an inch. Teaching it the corners again with the marker in its own grip fixed it. The mistake said exactly what was wrong.</p></aside>
    <footer class="band foot"><span class="strip" data-el="card 9 footer">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026</span><span class="counter">9 / 14</span></footer>
  </section>

  <section class="card split half trigger plate-blue" data-card="10" data-el="card 10 — the smart trigger that wasn't">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="../pitch/img/plate-3.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="wash" aria-hidden="true"></div>
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 10 kicker">10 · What broke</span><span class="wordmark" data-el="card 10 wordmark"><svg class="logo" viewBox="0 0 320 130" role="img" aria-label="Duet"><use href="#logo"/></svg></span></header>
    <div class="content">
      <div class="words">
        <h2 class="headline" data-el="card 10 headline">The smart trigger that wasn't.</h2>
        <p class="body" data-el="card 10 line 1">I wrote clever code so the robot would notice when you'd stepped back.</p>
        <p class="body" data-el="card 10 line 2">It fired every few seconds on an empty board.</p>
        <p class="body" data-el="card 10 line 3">Saturday morning I deleted it and added a button.</p>
        <p class="paper body takeaway" data-el="card 10 takeaway">The simple thing is allowed to win.</p>
      </div>
      <div class="figure"><span class="gobtn" data-el="card 10 the Go button">Go, robot!</span></div>
    </div>
    <aside class="notes" data-el="card 10 notes — the spoken part"><p>I was proud of this one before it broke: the robot would notice by itself, through the camera, when you had finished and stepped back. No button. At the table on Saturday it fired every few seconds on an empty board. I spent an hour on it, deleted it, and added a button that says Go, robot. The button worked all day and nobody missed the magic.</p></aside>
    <footer class="band foot"><span class="strip" data-el="card 10 footer">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026</span><span class="counter">10 / 14</span></footer>
  </section>

  <section class="card split half error plate-green" data-card="11" data-cut="20" data-el="card 11 — the error you'll get too">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="../pitch/img/plate-4.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="wash" aria-hidden="true"></div>
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 11 kicker">11 · What broke</span><span class="wordmark" data-el="card 11 wordmark"><svg class="logo" viewBox="0 0 320 130" role="img" aria-label="Duet"><use href="#logo"/></svg></span></header>
    <div class="content">
      <div class="words">
        <h2 class="headline" data-el="card 11 headline">The error you'll get too.</h2>
        <p class="body" data-el="card 11 line">Four spaces instead of eight. The day before the hackathon.</p>
        <p class="paper body takeaway" data-el="card 11 takeaway">The error message is the clue, not the insult.</p>
      </div>
      <div class="figure">
        <div class="paper codepanel" data-el="card 11 code — the excerpt"><pre>class Palletizer:
    def obstacles(self):
        boxes = self.placed_boxes()
    return WorldState(boxes)</pre></div>
        <p class="paper body errline" data-el="card 11 the error line">SyntaxError: 'return' outside function</p>
      </div>
    </div>
    <aside class="notes" data-el="card 11 notes — the spoken part"><p>The day before the hackathon, in the practice course: SyntaxError, return outside function. The return was right there under the function. Except it was four spaces in instead of eight, so Python thought the function had ended. Indentation is the structure. The message was telling me exactly that. Read it.</p></aside>
    <footer class="band foot"><span class="strip" data-el="card 11 footer">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026</span><span class="counter">11 / 14</span></footer>
  </section>

  <section class="card modules log plate-orange" data-card="12" data-cut="20" data-el="card 12 — the log">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="../pitch/img/plate-5.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="wash" aria-hidden="true"></div>
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 12 kicker">12 · The log</span><span class="wordmark" data-el="card 12 wordmark"><svg class="logo" viewBox="0 0 320 130" role="img" aria-label="Duet"><use href="#logo"/></svg></span></header>
    <div class="content">
      <div class="lead"><h2 class="headline" data-el="card 12 headline">I wrote down every problem.</h2></div>
      <ol class="mods four logfields">
        <li class="paper mod" data-el="card 12 field — symptom"><span class="num display">1</span><span class="body">Symptom</span></li>
        <li class="paper mod" data-el="card 12 field — what I tried"><span class="num display">2</span><span class="body">What I tried</span></li>
        <li class="paper mod" data-el="card 12 field — fix"><span class="num display">3</span><span class="body">Fix</span></li>
        <li class="paper mod" data-el="card 12 field — why it worked"><span class="num display">4</span><span class="body">Why it worked</span></li>
      </ol>
      <p class="closing body" data-el="card 12 line">Nine entries in two days.</p>
      <p class="paper body takeaway" data-el="card 12 takeaway">This is what debugging actually is.</p>
    </div>
    <aside class="notes" data-el="card 12 notes — the spoken part"><p>Every problem went in a log: what I saw, what I tried, what fixed it, why it worked. Nine entries in two days. Half of them I fixed by writing them down, because writing what you saw makes you look at it. Debugging is not being smart; it is being organized about being wrong. You could start one tomorrow.</p></aside>
    <footer class="band foot"><span class="strip" data-el="card 12 footer">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026</span><span class="counter">12 / 14</span></footer>
  </section>

  <section class="card split half felt plate-cream" data-card="13" data-el="card 13 — what it felt like">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="../pitch/img/plate-6.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="wash" aria-hidden="true"></div>
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 13 kicker">13 · What it felt like</span><span class="wordmark" data-el="card 13 wordmark"><svg class="logo" viewBox="0 0 320 130" role="img" aria-label="Duet"><use href="#logo"/></svg></span></header>
    <div class="content">
      <div class="words">
        <p class="headline" data-el="card 13 line 1">One person.</p>
        <p class="headline" data-el="card 13 line 2">Two days.</p>
        <p class="headline" data-el="card 13 line 3"><span class="key">Honorable mention.</span></p>
      </div>
      <figure class="paper photo figure" data-el="card 13 photo — the medal"><img src="img/medal.jpg" alt="Nicholas holding up the honorable mention medal at the Viam podium"></figure>
    </div>
    <aside class="notes" data-el="card 13 notes — the spoken part"><p>Most teams were two or three; I was one, with Claude as my teammate. I was tired. During the demo the room's WiFi kept dropping and the arm freezes when it drops; I stood there waiting for it to come back. It came back, and it drew. I didn't win. I got an honorable mention, and it was still the best two days I've had building something. I'd do it again tomorrow.</p></aside>
    <footer class="band foot"><span class="strip" data-el="card 13 footer">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026</span><span class="counter">13 / 14</span></footer>
  </section>

  <section class="card split advice plate-black" data-card="14" data-builds="2" data-el="card 14 — one piece of advice">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle-bright)"/></svg>
    <img class="plate-img" src="../pitch/img/plate-7.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="wash" aria-hidden="true"></div>
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 14 kicker">14 · One piece of advice</span><span class="wordmark" data-el="card 14 wordmark"><svg class="logo" viewBox="0 0 320 130" role="img" aria-label="Duet"><use href="#logo"/></svg></span></header>
    <div class="content">
      <div class="words">
        <p class="line reveal headline" data-step="1" data-el="card 14 line 1">You already know <span class="key">enough</span> to start.</p>
        <p class="line reveal headline" data-step="2" data-el="card 14 line 2">Start with the smallest thing that works, then make it bigger.</p>
      </div>
    </div>
    <aside class="notes" data-el="card 14 notes — the spoken part"><p>You already know enough to start. You know turtle; that is a robot with the motor taken out. Start with the smallest thing that works, then make it bigger. Mine was a square. Then a square the robot drew. Then a shape Claude chose. Then a whole drawing. Nobody starts with the whole drawing. Questions.</p></aside>
    <footer class="band foot"><span class="strip" data-el="card 14 footer">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026</span><span class="counter">14 / 14</span></footer>
  </section>
```

- [ ] **Step 4: Run the tests to see them pass**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: `# pass 19`, `# fail 0`. Then run the whole page suite: `node --test 'pagetests/*.test.mjs'` — every pitch test still passes.

- [ ] **Step 5: Check cards 9–14 and the cut in the browser**

Reload `http://localhost:8792/class/index.html#9`. Card 9: the "27 mm" fills the middle without pushing the takeaway past the frame (step `.big .display { --display: 12cqw }` down to `10cqw` if it does). Card 10: the Go button sits centered right. Card 11: the excerpt and the red error line both fit. Card 12: four numbered fields in a row. Card 13: the medal photo beside the three lines (if `img/medal.jpg` is not there yet the frame shows a broken image; that is expected until Nicholas supplies it). Card 14: two reveals, then End does nothing.

Then open `http://localhost:8792/class/index.html?cut=10`: ten cards, counter reads `n / 10`, kickers read `01`…`10`, cards 3, 9, 11 and 12 are gone, the reveals still work on the diner, setup, one-turn and advice cards, `0` jumps to the advice card. Then open `?notes=1`: the asides show as speech bubbles under the content and no card spills past its frame; if one does, step that card's tokens in `class.css` under a `.stage.shownotes .<card> { ... }` rule, as `deck.css` does.

Finally open the file directly, `open docs/duet/class/index.html`: it works over `file://` (font, plates, flipbook, clips).

- [ ] **Step 6: Commit**

```bash
git add docs/duet/class/index.html docs/duet/class/class.css code/hackathon/pagetests/class.test.mjs
git commit -m "feat(class): Act 3, what broke: the pen, the trigger, the error, the log, the medal, the advice

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 6: The talk-track

**Files:**
- Create: `docs/duet/class/talk.md`
- Modify: `code/hackathon/pagetests/class.test.mjs` (append)

- [ ] **Step 1: Append the failing test**

```js
test('talk.md: pre-flight, fourteen cards with times adding to about 17 minutes, the ten-minute list, the likely questions', () => {
  const t = read('talk.md');
  for (const line of ['## Pre-flight', '?cut=10', 'https://viam-duet.vercel.app', 'Optimize for video clip', '## The 10-minute version', '## Likely questions']) assert.ok(t.includes(line), line);
  const heads = [...t.matchAll(/^### (\d+) · .* \((\d+):(\d\d)\)/gm)];
  assert.equal(heads.length, 14, 'one heading per card with a time');
  assert.deepEqual(heads.map((m) => Number(m[1])), Array.from({ length: 14 }, (_, i) => i + 1));
  const total = heads.reduce((s, m) => s + Number(m[2]) * 60 + Number(m[3]), 0);
  assert.equal(total, 17 * 60 + 15, 'targets add to 17:15');
  for (const n of [3, 9, 11, 12]) assert.match(t, new RegExp(`^### ${n} · .*\\(cut in 10\\)`, 'm'), `card ${n} is marked cut`);
  for (const line of ['an AI that can look at a photo and tell you what\'s in it', 'Honorable mention', 'I didn\'t win', 'simplified',
    'You already know enough to start', 'Did you write all the code?', 'Could I build this?']) assert.ok(t.includes(line), `talk missing: ${line}`);
  assert.ok(!/motion service|inverse kinematics|WebRTC|polyline|inference/.test(t), 'no jargon');
});
```

- [ ] **Step 2: Run it to see it fail**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: 19 pass, 1 fails with `ENOENT ... talk.md`.

- [ ] **Step 3: Write `talk.md`**

Create `docs/duet/class/talk.md`:

```markdown
# A robot that draws back — the talk

For Carolina Uribe's class, grades 9 to 12, over Zoom or Meet. About twenty minutes of talk, then a Q&A rotation at the teacher's computer. Read this from a phone or a second window; the shared tab shows only the deck.

## Pre-flight

- [ ] Open `docs/duet/class/index.html` from disk in Chrome. If Carolina says ten minutes, open it as `index.html?cut=10` instead.
- [ ] Press **F** for fullscreen. Right arrow, space or a click on the right two thirds advances; left arrow or a click on the left third goes back; **1**–**9** and **0** jump; **Home**/**End**.
- [ ] Notes are off. (`?notes=1` shows them: rehearsal only, never on a share.)
- [ ] Second tab, already loaded: https://viam-duet.vercel.app (the replay, for the Q&A).
- [ ] Zoom: Share Screen → the Chrome window → tick "Optimize for video clip". Meet: share the window.
- [ ] Before class, step through cards 3 and 8 and confirm the four clips and the flipbook are playing on the shared screen.
- [ ] This file open on the phone.

## The 10-minute version

Cards 1, 2, 4, 5, 6, 7, 8, 10, 13, 14, with these targets: 1 (0:30), 2 (1:15), 4 (1:00), 5 (1:15), 6 (1:15), 7 (1:15), 8 (1:00), 10 (1:00), 13 (0:45), 14 (0:45) = 10:00. Open the deck with `?cut=10` and the cards below marked "(cut in 10)" are simply not there.

## The talk

Words in **bold** are on the card. Everything else is spoken. Times are targets, total 17:15, leaving room for chat questions.

### 1 · Duet (0:30)

**A robot that draws back. Two days at a robot hackathon.**

Hi, I'm Nicholas. I'm a friend of Ms. Uribe. Last weekend I spent two days at a robot hackathon in New York and built this: a robot arm that draws with you. You draw something, it looks at it, and it draws back. I'm going to show you what it is, how it works, and everything that went wrong on the way. Ask anything in the chat whenever you want. I can see it.

### 2 · What a hackathon is (1:30)

**Friday 9 am to Saturday 6 pm. Doors lock at night. / Teams of 2 or 3. A real robot arm each. / Demo at 3:30. Awards at 5.**

First, what's a hackathon? It's not a competition to hack into things. It's a weekend where a bunch of people show up to a room with a problem and try to build something real before the time runs out.

This one was run by Viam, a company that makes software for robots. They lent every team a real robot arm. That's the sign on the door. That's the room on demo day.

You get there Friday at 9 in the morning. They hand out the arms. At 9 at night they lock the doors, so no all-nighters. Saturday morning you come back, and at 3:30 in the afternoon everyone demos what they built. Awards at 5.

The theme was "fine motor skills": making a robot arm do delicate things. The suggested challenges were things like plug in a phone charger, pour water into a cup, stack Jenga blocks, sort recycling, move an egg without breaking it. Or bring your own idea. I brought my own.

### 3 · What other teams built (1:30) (cut in 10)

**Four clips.**

Here's what some other teams built. Same arm, same two days.

_(your line about clip 1)_
_(your line about clip 2)_
_(your line about clip 3)_
_(your line about clip 4)_

Different ideas, same two days. Every one of these started with somebody saying "what if it could..."

### 4 · Why I built this (1:30)

**My dad was an architect. He always had a pen. / At the diner, while we waited for the food, we'd draw together. / He'd draw. I'd draw on top. He'd draw again. Until the food came. / I didn't figure out that's where this came from until halfway through building it.**

Why did I build a robot that draws with you?

_(advance)_ My dad was an architect. He always had a pen.

_(advance)_ When I was a kid he'd take me to the diner, and while we waited for the food, we'd draw together on the placemat.

_(advance)_ He'd draw something. I'd draw on top of it. He'd draw again. Until the food came, and the drawing was done. That's how I got into art.

_(advance)_ Here's the strange part. I walked into the hackathon just thinking it would be fun to sketch with a robot. I didn't figure out where the idea came from until halfway through building it. I'd built the other side of that diner table.

### 5 · What Duet is (1:30)

**You draw. It looks. It thinks. It draws back.** Four callouts.

So this is the setup. That's the arm.

_(advance)_ On its wrist, that little box is a camera.

_(advance)_ Below it, the gripper, holding a green marker.

_(advance)_ On the table, the board. The red lines are a person's. The green lines are the robot's.

_(advance)_ And my laptop, running the code.

That's all of it. A camera, a hand, a marker, a board, a laptop.

### 6 · One turn (1:30)

**LOOK · THINK · DRAW.** Claude's sentence. **8 seconds to look and decide.**

One turn goes like this.

_(advance)_ LOOK. You draw something and press Go. The camera takes a photo of the board.

_(advance)_ THINK. The photo goes to Claude. Claude is an AI that can look at a photo and tell you what's in it. I ask it two questions: what do you see, and what would you add? This is a real answer from the hackathon: "A crowded world of creatures, flowers and dancing figures. A small green dancing figure in the open lower-right space to balance the crowd." That took about eight seconds.

_(advance)_ DRAW. Claude doesn't just say it. It also sends the shape it wants to draw as a list of points. The arm follows the points, and the green figure appears. Then it's your turn again.

### 7 · It's just points (1:30)

**Your turtle and my robot follow the same thing: a list of points.** Two code panels.

Now here's the part I really want you to see, because Ms. Uribe told me you're drawing in Python right now.

On the left is turtle. You've written this. Pen up. Go to the start. Pen down. Then go through a list of points. Pen up.

On the right is my robot. I simplified it a little, but that's the shape of it. Pen up. Move to the start. Pen down. Go through a list of points. Pen up.

It's the same program. Your turtle and my robot follow the same thing: a list of points. Mine has a motor. Everything you've learned about drawing with code is exactly what the robot does. The rest is plumbing.

### 8 · Watch it (1:30)

The flipbook. **Play with it after: viam-duet.vercel.app**

Here's a whole session. Ten turns. Red is the person. Green is the robot. Watch it grow.

_(let it loop once, about fifteen seconds; say nothing)_

Every green line is the robot answering a red one.

There's a version of this you can play with on the web after class, at viam-duet.vercel.app. It replays a real session, with what Claude said at every turn.

### 9 · The robot crushed the pen (1:15) (cut in 10)

**27 mm. The robot crushed the pen.** … **Measure with the robot's hand, not yours.**

OK. What broke. Because plenty did.

The very first line the robot drew, it pushed the marker so hard it flattened the tip. Crushed it.

Why? To tell the robot where the board is, I'd touched the marker to the corners of the board. With the marker in my hand. But the robot holds the marker differently than I do. 27 millimeters differently. That's more than an inch. So it drove the pen an inch into the board.

The fix: teach it the corners again, with the marker in the robot's grip. The mistake told me exactly what was wrong. Measure with the robot's hand, not yours.

### 10 · The smart trigger that wasn't (1:15)

**The smart trigger that wasn't.** Three lines. **Go, robot!** … **The simple thing is allowed to win.**

Second one. I was proud of this one, before it broke.

I wrote clever code so the robot would notice, by itself, using the camera, when you'd finished drawing and stepped back. No button. Magic.

Saturday morning at the table, it fired every few seconds on a completely empty board. The robot kept trying to take its turn when nobody had drawn anything. I spent an hour on it.

Then I deleted the whole thing and added a button that says "Go, robot!" You draw, you press Go. The button worked all day. It was in the demo. Nobody missed the magic. The simple thing is allowed to win.

### 11 · The error you'll get too (1:00) (cut in 10)

**The error you'll get too.** The excerpt. **SyntaxError: 'return' outside function.** … **The error message is the clue, not the insult.**

And one you're going to get too. The day before the hackathon I was doing the practice course, and I got this: SyntaxError, 'return' outside function.

I stared at it. The return was right there under the function. Except it wasn't. It was four spaces in instead of eight. Python thought the function had already ended. In Python, indentation isn't decoration; it's the structure.

The error message was telling me exactly that. The error message is the clue, not the insult. Read it.

### 12 · The log (0:45) (cut in 10)

**I wrote down every problem.** Symptom · What I tried · Fix · Why it worked. **Nine entries in two days.** … **This is what debugging actually is.**

One thing I did that I'd tell anyone to do. I wrote down every problem. What I saw. What I tried. What fixed it. Why it worked. Nine entries in two days.

Half of them I fixed by writing them down, because writing down what you saw makes you actually look at what you saw. That is what debugging actually is. Not being smart. Being organized about being wrong. You could start one tomorrow.

### 13 · What it felt like (1:15)

**One person. Two days. Honorable mention.** The medal.

What it felt like. One person, two days. Most teams were two or three people. I was one, with Claude as my teammate.

I was tired. During the demo the WiFi in the room kept dropping, and the arm freezes when it drops. I stood there with my hands shaking, waiting for it to come back. And it came back, and it drew.

I didn't win. I got an honorable mention. That's this medal. And it was still the best two days I've had building something. I'd do it again tomorrow.

### 14 · One piece of advice (0:45)

**You already know enough to start. / Start with the smallest thing that works, then make it bigger.**

So, the one thing I'd tell you.

_(advance)_ You already know enough to start. You know turtle. That's a robot with the motor taken out.

_(advance)_ Start with the smallest thing that works, then make it bigger. Mine was a square. Then a square the robot drew. Then a shape Claude chose. Then a whole drawing. Nobody starts with the whole drawing.

Questions.

## Likely questions

For the rotation at the teacher's computer. One-line answers; edit them before the talk.

- **Did you write all the code?** I designed it and decided everything. Claude wrote a lot of it with me. I still had to understand every piece to fix it when it broke, and it broke a lot.
- **How much did it cost?** The arm was lent for the weekend. Claude cost a few dollars for two days of turns.
- **Can it draw anything?** It draws what it decides to add to what you drew, in simple shapes. It's a partner, not a printer.
- **Did it ever hit anything?** No. The software knows where the table and the wall are and plans around them, and there's a big red emergency-stop button.
- **Could I build this?** The drawing part, yes, this month, in turtle. The robot part is the same code with a motor.
- **Why a robot and not just a screen?** Because it makes a real mark you keep.
- **What was the hardest part?** Getting the pen to touch the board at exactly the right height.
- **What would you do next?** Let you teach it your own drawing style from a stack of your sketches.
```

- [ ] **Step 4: Run the test to see it pass**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: `# pass 20`, `# fail 0`.

- [ ] **Step 5: Commit**

```bash
git add docs/duet/class/talk.md code/hackathon/pagetests/class.test.mjs
git commit -m "docs(class): the talk-track, with pre-flight, the ten-minute version and likely questions

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 7: README, final verification, and the whole suite

**Files:**
- Create: `docs/duet/class/README.md`
- Modify: `code/hackathon/pagetests/class.test.mjs` (append)

- [ ] **Step 1: Append the failing test**

```js
test('README: how to open it, the keys, the cut, the notes, the assets, and what stays out of git', () => {
  const r = read('README.md');
  for (const line of ['open docs/duet/class/index.html', '?cut=10', '?notes=1', 'build_assets.py', 'hackathon-videos/', 'crowd.jpg', 'medal.jpg', 'video/', 'node --test']) {
    assert.ok(r.includes(line), `README missing: ${line}`);
  }
});
```

- [ ] **Step 2: Run it to see it fail**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: 20 pass, 1 fails with `ENOENT ... README.md`.

- [ ] **Step 3: Write the README**

Create `docs/duet/class/README.md`:

```markdown
# Duet class deck

Fourteen cards, about twenty minutes, for Carolina Uribe's 9th to 12th grade Python class. The talk is in `talk.md`.
Spec: `docs/superpowers/specs/2026-09-21-class-deck-design.md`.

Open it (offline is fine; the font, the plates and the flipbook photos come from `../pitch/`):

    open docs/duet/class/index.html

Keys: Right, space, or a click on the right two thirds advances (through a card's reveals first); Left or a click on the
left third goes back; 1 to 9 and 0 jump to cards 1 to 10; Home and End; F fullscreen; D developer mode (hover shows an
element's name, click copies it).

`index.html?cut=10` is the ten-minute version: the cards marked `data-cut="20"` (3, 9, 11, 12) are dropped and the rest
renumbered. `?notes=1` shows each card's spoken part under it, for rehearsal only; never on a screen-share.

## Assets

Sources live in `hackathon-videos/` at the repo root (untracked). Build the deck's copies with the hackathon venv:

    cd docs/duet/class && ../../../code/hackathon/.venv/bin/python build_assets.py

It converts the four photos to `img/*.jpg` and the four clips to `video/team-N.mp4` (H.264, 720 px tall, muted, at most
15 s), skipping outputs that exist (`--force` redoes them).

The repo is public, so these stay local: `video/` (other teams' projects) and `img/crowd.jpg`, `img/medal.jpg` (people who
were not asked). They are gitignored along with `hackathon-videos/`. A fresh clone shows card 3 empty and card 13 without
its photo until the sources are dropped in and the script is run.

Checks: `cd code/hackathon && node --test 'pagetests/*.test.mjs'` and `.venv/bin/python -m pytest -q tests/test_class_assets.py`
```

- [ ] **Step 4: Run the whole suite**

Run (from `code/hackathon`): `node --test 'pagetests/*.test.mjs'`
Expected: every test passes, `class.test.mjs` contributing 21, `pitch.test.mjs` unchanged.

Run (from `code/hackathon`): `.venv/bin/python -m pytest -q`
Expected: the whole hackathon suite passes, including `tests/test_class_assets.py`.

- [ ] **Step 5: Final browser pass and screenshots**

With the `class` preview on `http://localhost:8792/class/index.html`: step through all fourteen cards with the keyboard, then `?cut=10` through all ten, checking on every card that nothing crosses the frame, that reveals work forward and back, that card 3's clips play and card 8's flipbook runs, that the console has no errors (a 404 for `img/medal.jpg` is expected until the photo is supplied). Take one screenshot each of cards 1, 5, 6, 7, 10 and 13 for the summary. Then `open docs/duet/class/index.html` and step through once over `file://`.

- [ ] **Step 6: Commit**

```bash
git add docs/duet/class/README.md code/hackathon/pagetests/class.test.mjs
git commit -m "docs(class): README for the class deck

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

- [ ] **Step 7: Report**

Tell Nicholas: what was built, the test counts, the screenshots, and the two things still his: `hackathon-videos/photo-medal.jpg` (then rerun `build_assets.py`) and the four captions for card 3 (the `card 3 caption — team N` paragraphs in `index.html` and the four `_(your line about clip N)_` lines in `talk.md`). Do not open a PR; he decides when.
