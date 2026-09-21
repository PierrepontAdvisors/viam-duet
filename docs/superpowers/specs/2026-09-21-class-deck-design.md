# Class deck: "A robot that draws back" — design

Date: 2026-09-21. Status: approved in brainstorming, ready for an implementation plan.
Related: `docs/duet/pitch/` (the seven-card hackathon deck this reuses), `docs/superpowers/specs/2026-09-19-duet-pitch-deck-design.md`, `notes/hackathon/06-story.md`, `notes/stuck-log.md`, `notes/hackathon/04-plan.md`.

## 1. Purpose

A fourteen-card HTML deck and a written talk-track for a ~20-minute talk Nicholas gives over Zoom or Google Meet to Carolina Uribe's high-school class (grades 9–12, mostly 9th graders, currently learning to draw in Python before moving on to AI and robotics). Students ask through chat during the talk; afterwards three to five students come to the teacher's computer one at a time to ask their own questions.

Carolina asked for eight things, and the biggest one is the frame: computer science is not completing coding exercises; you can use code, AI and technology to make things, experiment, solve problems and bring an idea to life. The eight: what a hackathon is and what the challenge was; what he built and why; very simply, how computer vision plus Claude drew with a person turn by turn; how it went from idea to working; something that failed and what changed to fix it (the class has been talking about debugging and how mistakes give information); the project working, on video; what it felt like to build in two days and get recognized; one piece of advice for beginners who think they are nowhere near this.

The deck must open from disk with no network, screen-share cleanly, and look like the Duet pitch deck so the two read as one body of work.

## 2. Decisions from brainstorming

- **A new deck, not the pitch deck.** The pitch deck is two minutes for adults. This one is twenty minutes for 14-year-olds. It reuses the pitch's visual system and nothing of its copy.
- **Designed for 20 minutes with a real 10-minute cut.** The slot length is not confirmed. Ten of the fourteen cards form the short version, and the deck can be opened in that form (section 5), not just skipped through.
- **Three acts, the loop as the spine.** Act 1, the room: what a hackathon is, what other teams built, why he built this. Act 2, the machine: what Duet is, one turn, it's just points, watch it. Act 3, what broke: three failures in the order they happened, the log, what it felt like, one piece of advice.
- **The diner story is the "why," early, not the close.** Kids need the why before the how.
- **One code card, side by side.** A turtle square next to Duet's stroke loop. Nothing else on screen is code except the error message on card 11.
- **Card 8 is the pitch's flipbook, not an mp4.** Same frames, one second a turn, with the "you / Duet" label under each. No transcoding.
- **The live replay site is for the Q&A rotation**, preloaded in a second tab, not shown during the talk.
- **Honorable mention, said exactly that way.** "I didn't win. I'd do it again tomorrow."
- **Advice line:** "You already know enough to start. Start with the smallest thing that works, then make it bigger."
- **The four clips of other teams and the two photos with identifiable people stay out of git.** The repo is public.
- **The text-only cards tell their story in pictures** (added 2026-09-21 afternoon, Nicholas's goal): cards 4, 9, 10, 11, 12 and 14 carry cartoon pictures generated in the pitch's grammar (thick marker outline, flat fills, no text, Nano Banana 2 via `gen_images.py`), on paper panels across the top of the card, with the words under them. Cards with reveals (4, 14) reveal one panel and its caption per advance, like a comic strip.
- **Notes for rehearsal only.** Over a screen-share the pitch's in-card notes would be visible to the class, so the talk is read from `talk.md` on a phone or second window.

## 3. The cards

Words in quotes are on the slide. Everything else is spoken, and the spoken words live in `talk.md` (section 4). "Plate" means one of the pitch's seven background plates, cycling: card n uses plate ((n − 1) mod 7) + 1. Card 4 is the exception: `plate-black`, the pitch's card 7 plate, white type. ★ marks the ten cards of the 10-minute cut. "Reveals" are advance steps within the card before it moves on.

**Act 1 · The room**

1. ★ **Title.** Full-bleed hero: `img/setup.jpg` (the arm over the board, the laptop). Kicker "01 · Duet". Headline "A robot that draws back." Sub-line "Two days at a robot hackathon." Nicholas says who he is in one line and what they're about to see.

2. ★ **What a hackathon is.** Two photos side by side: `img/door.jpg` (the "Please, check in before hacking" sign) and `img/crowd.jpg` (demo day). Kicker "02 · What a hackathon is". Three short lines under the photos: "Friday 9 am to Saturday 6 pm. Doors lock at night." · "Teams of 2 or 3. A real robot arm each." · "Demo at 3:30. Awards at 5." Spoken: the challenge was "fine motor skills" (plug in a charger, pour water, stack Jenga, sort recycling, move an egg) or bring your own idea; "I brought my own."

3. **What other teams built.** Kicker "03 · What other teams built". Four portrait clips in a single row, each about three quarters of the card height, `video/team-1.mp4` to `team-4.mp4`, each `muted loop playsinline preload="auto"` (no `autoplay`: `class.js` plays them when card 3 is shown and pauses them when it is not). A one-line caption under each (an input Nicholas supplies, section 6). Spoken: one line per team.

4. ★ **Why I built this.** Black card (`plate-black`, plate-7). Kicker "04 · Why I built this". A strip of four square cartoon panels, each a paper card with its line as the caption under the picture, revealed one per advance: `story-4-1` (the architect in a diner booth, a marker behind his ear, a rolled drawing under his arm) "My dad was an architect. He always had a pen." · `story-4-2` (the two of them across a diner table, markers over a placemat) "At the diner, while we waited for the food, we'd draw together." · `story-4-3` (a big hand and a small hand drawing one loopy line on the placemat as the fries arrive) "He'd draw. I'd draw on top. He'd draw again. Until the food came." · `story-4-4` (the kid across the table from a green robot arm, both drawing) "I didn't figure out that's where this came from until halfway through building it." Reveals: 4.

5. ★ **What Duet is.** Kicker "05 · What Duet is". Headline "You draw. It looks. It thinks. It draws back." `img/setup.jpg` large with four numbered callouts placed over the photo (dot plus label, positions in percent of the photo, set in `class.css`), revealed one per advance: "1 · a camera on the wrist" · "2 · a gripper holding a green marker" · "3 · the board: red is a person, green is the robot" · "4 · the laptop running the code". Reveals: 4.

6. ★ **One turn.** Kicker "06 · One turn". The pitch's triptych layout; each advance reveals one module together with the verb over it, left to right: **"LOOK"** over `../pitch/img/turn-07-human.jpg` (caption "the camera takes a photo"); **"THINK"** over a speech bubble with Claude's real sentence, "A crowded world of creatures, flowers and dancing figures." / "A small green dancing figure in the open lower-right space to balance the crowd." and the pill "8 seconds to look and decide"; **"DRAW"** over `../pitch/img/turn-07-robot.jpg` (caption "the arm follows the points"). Reveals: 3. Spoken: Claude is "an AI that can look at a photo and tell you what's in it" (the only time the word needs explaining).

7. ★ **It's just points.** Kicker "07 · It's just points". Headline "Your turtle and my robot follow the same thing: a list of points." Two code panels side by side, monospace, one label each.
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
   The right panel is a faithful simplification of `code/hackathon/duet/controller.py` `_stroke()` (travel to the first point lifted, lower, move through every point, lift). The talk-track says it is simplified. Spoken close: "Mine has a motor."

8. ★ **Watch it.** Kicker "08 · Watch it". The pitch's flipbook: the 21 photos of session 20260919-151119 from `../pitch/img/` (`turn-00-start.jpg`, then `turn-NN-human.jpg` / `turn-NN-robot.jpg` for turns 1 to 10), 700 ms a frame, 2 s hold on the last, with the label "turn n of 10 · you / Duet" under the frame, looping while the card is up. One line under it: "Play with it after: viam-duet.vercel.app". Spoken: "ten turns; every green line is the robot answering a red one."

**Act 3 · What broke**

9. **The robot crushed the pen.** Kicker "09 · What broke". One 16:9 cartoon panel on top, `story-9` (a green robot arm pressing a red marker into a whiteboard so hard the tip squashes flat). Under it: headline "The robot crushed the pen.", the line "I measured the board with the marker in my hand. The robot holds it 27 mm differently.", and the takeaway, set apart: "Measure with the robot's hand, not yours." Source: stuck-log 2026-09-18, "pen crushed the felt on the first square."

10. ★ **The smart trigger that wasn't.** Kicker "10 · What broke". Two square cartoon panels on top: `story-10-1` (the robot arm with its wrist camera hovering over an empty board, question marks around it) and `story-10-2` (a kid pressing a big green button while the arm happily draws). Under them: headline "The smart trigger that wasn't.", three lines run together as one paragraph, "I wrote clever code so the robot would notice when you'd stepped back." · "It fired every few seconds on an empty board." · "Saturday morning I deleted it and added a button." followed inline by a small green button in the page's style reading "Go, robot!", then the takeaway: "The simple thing is allowed to win." Source: 04-plan "Trigger, day 2 at the table."

11. **The error you'll get too.** Kicker "11 · What broke". Two panels on top: `story-11` (a kid squinting at a laptop where one line of code sticks out and a red burst pops from the screen) and, beside it as the second panel, the code excerpt on paper with the error line under it in red:
    ```
    class Palletizer:
        def obstacles(self):
            boxes = self.placed_boxes()
        return WorldState(boxes)
    ```
    `SyntaxError: 'return' outside function`. Under the panels: headline "The error you'll get too.", the line "Four spaces instead of eight. The day before the hackathon.", the takeaway "The error message is the clue, not the insult." Source: stuck-log 2026-09-17, first entry. (The excerpt is an illustration of that entry's bug, not a verbatim copy of `palletizer.py`.)

12. **The log.** Kicker "12 · The log". One 16:9 cartoon panel on top, `story-12` (a hand filling four boxes in a notebook with a marker, the robot arm in the background). Under it: headline "I wrote down every problem.", the four fields as a row of pills, "1 Symptom" · "2 What I tried" · "3 Fix" · "4 Why it worked", the line "Eight entries by Friday night." (the stuck log holds three entries from the practice day and five from the Friday), the takeaway "This is what debugging actually is." Spoken: the class can start one tomorrow.

13. ★ **What it felt like.** Kicker "13 · What it felt like". `img/medal.jpg` large (Nicholas with the medal at the Viam podium). Three lines: "One person." · "Two days." · "Honorable mention." Spoken: tired; the venue WiFi kept dropping during the demo; it drew anyway; "I didn't win. I'd do it again tomorrow."

14. ★ **One piece of advice.** Kicker "14 · One piece of advice". Black card. Two 16:9 cartoon panels, each with its line as a headline-sized caption under the picture, revealed one per advance: `story-14-1` (a kid at a laptop where a turtle draws a square, and a tiny robot arm drawing the same square) "You already know enough to start." · `story-14-2` (four whiteboards growing from one small square to a crowded drawing, the kid climbing them like stairs) "Start with the smallest thing that works, then make it bigger." Reveals: 2. Spoken close: "Questions."

**Master page.** Every card carries the pitch's chrome: frame, kicker, the Duet wordmark, the footer strip "Nicholas Fjellberg Swerdlowe · Viam Fine Motor Skills Hackathon · 2026" and a counter "n / 14" (or "n / 10" in the cut, section 5).

**10-minute cut:** cards 1, 2, 4, 5, 6, 7, 8, 10, 13, 14. Cards 3, 9, 11 and 12 carry `data-cut="20"`.

## 4. The talk-track (`docs/duet/class/talk.md`)

One Markdown file Nicholas reads from a phone or a second window while the deck is shared.

- **Voice rules.** Short sentences. Present tense for the machine, past tense for the two days. Words a 9th grader has: no "motion service," "IK," "WebRTC," "polyline," "inference." "Claude" is explained once, on card 6. Names Viam once, on card 2 ("a company that makes software for robots; they lent the arms").
- **Per card:** the card's on-slide words (so he can see what the class sees), then what he says, then a target time. Targets: 1 (0:30), 2 (1:30), 3 (1:30), 4 (1:30), 5 (1:30), 6 (1:30), 7 (1:30), 8 (1:30), 9 (1:15), 10 (1:15), 11 (1:00), 12 (0:45), 13 (1:15), 14 (0:45). Total 17:15, leaving slack for chat questions. Cards outside the cut are marked "(cut in 10)" in their heading, and the 10-minute version's per-card targets are listed once at the top: 1 (0:30), 2 (1:15), 4 (1:00), 5 (1:15), 6 (1:15), 7 (1:15), 8 (1:00), 10 (1:00), 13 (0:45), 14 (0:45) = 10:00.
- **The truth beats to keep.** "One person" (teams were 2–3; he built alone). The failures are told as what happened, in the order they happened. Card 7's robot code is called "simplified." Honorable mention, not a win.
- **Pre-flight checklist** at the top: open `docs/duet/class/index.html` from disk in Chrome (`?cut=10` if the slot is ten minutes); press F for fullscreen; the replay at https://viam-duet.vercel.app open in a second tab for the Q&A; Zoom or Meet share set to optimize for video; the four clips on card 3 and the flipbook on card 8 confirmed playing before class; `talk.md` open on the phone; notes off in the shared tab.
- **Likely questions** at the bottom, one-line answers each, for the Q&A rotation: Did you write all the code? (I designed it and decided everything; Claude wrote a lot of it with me; I still had to understand every piece to fix it when it broke.) · How much did it cost? (The arm was lent for the weekend; Claude cost a few dollars for two days of turns.) · Can it draw anything? (It draws what it decides to add to what you drew, in simple shapes; it's a partner, not a printer.) · Did it ever hit anything? (No; the software knows where the table and wall are and plans around them, and there's a red emergency-stop button.) · Could I build this? (The drawing part, yes, this month, in turtle. The robot part is the same code with a motor.) · Why a robot and not just a screen? (Because it makes a real mark you keep.) · What's the hardest part? (Getting the pen to touch the board at exactly the right height.) Nicholas edits the answers before the talk.

## 5. Build

**Files**, all under `docs/duet/class/`:

- `index.html`: the fourteen cards, one `<section class="card" data-card="n" data-el="card n — name">` each, in order, following the pitch's markup (kicker, wordmark, content, footer with counter, an `<aside class="notes">` per card for rehearsal). Links `../pitch/fredoka.css`, `../pitch/deck.css`, `class.css`, `class.js`, `../pitch/dev.js`. Opens over `file://`.
- `class.css`: only what the pitch's CSS lacks: the two-photo card (2), the row of four portrait videos (3), photo callouts (5), the verb labels over the triptych (6), the two code panels (7), the three-line photo card (13), and the `story` template for the text-only cards (4, 9, 10, 11, 12, 14): a `.strip` of one, two or four `.panel` paper cards (picture, optional caption) across the top, and an `.under` column for the words; the strips step down under `.stage.shownotes`. Every font size is a bare token from `deck.css` (redefine `--caption`/`--body` on the element rather than writing a size), the pitch's rule.
- `class.js`: navigation for this deck. It is decided in the plan, after reading `deck.js`, whether this is a trimmed copy of `deck.js` with the class constants or `deck.js` made to read its card count, reveals and flipbook from the page. Either way `docs/duet/pitch/` behaves exactly as before (its tests guard that). Behaviour: Right, space, click on the right two thirds advance (through reveals first); Left, click on the left third go back; 1–9 jump to cards 1–9 and 0 to card 10; Home, End; F fullscreen; D developer mode; `#n` in the hash. Pure state functions (`advance`, `back`, `jump`, `parseHash`, `flipLabel`, `flipDelay`, `nextFlip`) hang off `window.ClassDeck` so the Node tests load the file without a DOM. No autoplay Play pill or Speed dropdown; this deck is only ever talked through. The flipbook runs while card 8 is shown and stops when it is not. `class.js` calls `play()` on the four card-3 videos when card 3 becomes the shown card and `pause()` when it stops being, so four decoders are not running behind card 1.
- **`?cut=10`:** before init, `class.js` removes every card with `data-cut="20"` from the DOM, renumbers `data-card` and the counters 1..10, and reads reveals from the surviving cards, so the cut deck is a real ten-card deck with a "n / 10" counter. The pure functions take the card count as an argument.
- `talk.md`: section 4.
- `build_assets.py`: converts the source photos and clips (section 6). Run with the hackathon venv (Pillow 12 is installed there; ffmpeg 9 is on the path). Idempotent; skips outputs that exist; `--force` redoes them.
- `README.md`: how to open it, the keys, `?cut=10`, how to rebuild assets, and which files are local-only and why.
- `img/`: `setup.jpg`, `door.jpg`, `crowd.jpg`, `medal.jpg` (the last two gitignored).
- `video/`: `team-1.mp4` to `team-4.mp4` (gitignored).

**`.claude/launch.json`:** a `class` entry serving `docs/duet` on port 8792 (so `../pitch/` resolves), used for verification in the browser pane; open `/class/index.html`.

**Developer mode:** the pitch's `dev.js`, unchanged; every meaningful element carries a unique, specific `data-el` name in the pitch's style ("card 6 verb — LOOK", "card 3 video — team 2").

## 6. Assets and privacy

Sources are in `hackathon-videos/` at the repo root (untracked; Nicholas's drop folder):

| Source | Output | How |
|---|---|---|
| `photo-setup.webp` | `img/setup.jpg` | Pillow, longest side 2000 px, JPEG q85 |
| `photo-door.webp` | `img/door.jpg` | same |
| `photo-crowd.webp` | `img/crowd.jpg` | same; gitignored |
| `photo-medal.jpg` (Nicholas supplies) | `img/medal.jpg` | same; gitignored |
| `IMG_0016.MOV` | `video/team-1.mp4` | ffmpeg: H.264, 720 px tall, no audio, at most 15 s, `+faststart`; gitignored |
| `IMG_0018.mov` | `video/team-2.mp4` | same |
| `IMG_0022.mov` | `video/team-3.mp4` | same |
| `IMG_0024.mov` | `video/team-4.mp4` | same |

Clip order is by filename (chronological). `build_assets.py` holds this table.

**Story pictures** (committed, about 2 MB): `img/story-4-1.jpg` … `story-4-4.jpg`, `story-9.jpg`, `story-10-1.jpg`, `story-10-2.jpg`, `story-11.jpg`, `story-12.jpg`, `story-14-1.jpg`, `story-14-2.jpg`, generated by `docs/duet/class/gen_images.py` with Nano Banana 2 (`gemini-3.1-flash-image`, 1K) in the pitch's cartoon grammar: it imports the pitch's generator for the endpoint, key lookup and JPEG conversion, and holds only the jobs. `GEMINI_API_KEY` from the environment wins over `code/hackathon/.env` (a worktree has no `.env`). Prompts describe the scene and the stroke grammar and never name an artist, the pitch's rule. Regenerate one with `python3 docs/duet/class/gen_images.py --force story-9`.

**`.gitignore` additions:** `hackathon-videos/`, `docs/duet/class/video/`, `docs/duet/class/img/crowd.jpg`, `docs/duet/class/img/medal.jpg`. Reason, stated in the class README: the repo is public; the clips are other teams' work and the two photos show identifiable people who were not asked. The arm and door-sign photos commit.

**Inputs Nicholas supplies before the build is complete:** `hackathon-videos/photo-medal.jpg`; four one-line captions for card 3 (what each team built). Until the captions arrive the card ships with the captions empty and the talk-track marks the gap; the copy test does not cover them.

## 7. Tests

`code/hackathon/pagetests/class.test.mjs`, run by the existing `node --test 'pagetests/*.test.mjs'` from `code/hackathon`, mirroring `pitch.test.mjs`:

- Fourteen cards in order with the agreed copy: the headline of every card, the four diner lines, the four callouts, LOOK · THINK · DRAW, Claude's two sentences, "8 seconds to look and decide", both code panels verbatim, the `SyntaxError` line, the four log fields, "Honorable mention.", both advice lines, "viam-duet.vercel.app". Plain apostrophes.
- Cards 3, 9, 11, 12 carry `data-cut="20"` and no others do.
- Reveals: card 4 has 4, card 5 has 4, card 6 has 3, card 14 has 2; `advance`/`back`/`jump` behave at 14 cards and at 10, never mutate their input.
- `parseHash`; the flipbook lists the 21 photos in turn order, labels them, holds on the last.
- Every `<video>` on card 3 is `muted`, `loop`, `playsinline`, has no `autoplay`, and there are four.
- The story cards: card 4 has four `panel paper reveal` figures with steps 1–4 and the four lines as captions; card 14 two; cards 9, 10, 11, 12 reference their pictures; the eleven `story-*.jpg` exist; `gen_images.py` exists, holds every job name, keeps the key out of the repo, and never names an artist.
- Every local file the deck references exists, except the six gitignored assets, which are instead asserted to be covered by `.gitignore` (so a fresh clone of the public repo passes).
- Developer mode wired: badge, label, toast, unique `data-el` names across all cards.
- Every card carries the master page: frame, kicker, wordmark, footer with a counter.
- `class.css` has no font size that is not a token.
- `pitch.test.mjs` still passes unchanged.

Browser verification (not automated): the `class` launch entry, `?cut=10` shows ten cards with a "n / 10" counter, card 3 plays four clips, card 8 flips, the D key works, no console errors, and the deck also opens directly from `file://`.

## 8. Git

Work happens in the worktree `.worktrees/class-deck` on `feat/class-deck` (from `origin/main`); the shared checkout stays on `feat/duet-design` and is never switched. Small conventional commits. Merge by squash-merge PR like the rest of the repo. The public-repo audit rules apply: no personal paths, no keys, no tracking tokens.

## 9. Out of scope

- Publishing the class deck to viam-duet.vercel.app (could be added later as `site/class/`; not needed for a screen-share).
- A synced presenter view; an mp4 of the session; the pitch's autoplay Play pill and Speed dropdown; new generated plates or heroes (the pitch's seven plates are reused).
- Any change to the pitch deck's copy or behaviour.
