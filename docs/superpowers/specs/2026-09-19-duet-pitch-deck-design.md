# Duet pitch deck: design

Date: 2026-09-19. Status: approved in brainstorming, ready for an implementation plan.
Related: `docs/duet/PRD-duet.md`, `docs/superpowers/specs/2026-09-18-duet-design.md`, `docs/superpowers/specs/2026-09-18-duet-page-design.md`.

## 1. Purpose

A seven-card HTML slide deck that Nicholas talks through for about two minutes at the Fine Motor Skills hackathon demos (2026-09-19, 3:30 PM), then walks to the board and draws. The deck carries the origin story; the robot carries the proof. The deck must open from disk with no network and look like the live Duet page, so the two read as one thing.

Decisions made during brainstorming:

- **Deck first, then live demo.** The deck is not a leave-behind and does not run while the arm draws.
- **The companion claim is "a partner who answers in their hand."** Claude is the mind that looks and decides; the artist is the language it answers in. The deck never claims the painter is present. The word "with" carries the weight.
- **The opening is the thesis as a line**, not a photo and not a blank board.
- **Co-creation is the headline; learning is the second beat.** Inspiration and technique are said, not given a card.
- **One technical card**, with Viam named in every step it touches.
- **The close is the build itself** ("One person. Two days. Claude and Viam."), with the rig instruction as its footer so it stays on screen during the demo. "One person" is accurate.
- **One self-contained HTML file**, no framework, no CDN, no build step.
- **The look is bright Haring plates**, not the page's black stage: each card sits on a saturated colour plate covered in a repeating squiggle pattern in Keith Haring's style, with bold black type. Added after the first spec read.
- **Generated images do two jobs** (added 2026-09-19 late morning): seven background plate textures and three hero illustrations, made with Nano Banana 2 (`gemini-3.1-flash-image`) through the Gemini API. The inline SVG squiggle pattern stays underneath every plate as the fallback, so the deck works if a generation is missing or poor. Prompts describe the stroke grammar and never name the artist, the same rule the PRD sets for the robot.

## 2. The cards

Words in quotes are on the slide. Everything else is spoken.

**Card 1, Thesis.** Yellow plate. Three lines, black, revealed one per advance:
"Anyone can now study with the greatest minds in history."
"Nobody could make art with them."
"Until today."

**Card 2, What Duet is.** The wordmark "Duet", then "A robot arm that draws with you." Three short lines: "You make a mark." / "It looks, understands, and answers." / "In the hand of an artist you choose." Three chips, each with a small drawn stroke sample: Van Gogh (curved dashes in a swirl), Mondrian (straight horizontal and vertical lines with a hatched cell), Keith Haring (a bold outline with radiating ticks). Spoken: Claude is the mind that looks at the photo and decides; the artist is the language it answers in.

**Card 3, One turn.** Two photos side by side on white paper cards: `turn-01-human.jpg` (your mark) and `turn-01-robot.jpg` (the answer) from session `20260918-190258`. A speech bubble in the page's style holds Claude's two sentences exactly as recorded in that session's `session.json`:
"A big bold amoeba-like creature with loops and eye-holes sprawls across the board."
"I'll add a small green spiral accent inside the lower loop body to give the creature a pulsing core."
A small badge: "8 s to look and decide." (day 1 measured 7.4 to 7.6 s live; the deck uses the same rounded number everywhere). Exchange 1 was chosen because later exchanges' sentences contain millimetre coordinates and quotes are not edited.

**Card 4, Co-creation (the headline).** "Everyone leaves with a one-of-a-kind piece, made with a partner." Below it, a flipbook of the 13 photos from the same session (`turn-00-start.jpg`, then `turn-NN-human.jpg` and `turn-NN-robot.jpg` for NN 01 to 06), about 0.7 s per photo, a 2 s hold on the last, then loop. A small counter beside it reads "turn N of 6" (the start photo reads "start"). Under the flipbook: "Six exchanges. Two artists. One of them was a robot."

**Card 5, Learning.** "And you learn their language by answering back." Three lines, each with its artist chip:
Haring: "One continuous outline, then motion ticks. Your blob becomes a figure."
Mondrian: "Your mark's edges run out to a grid. You start seeing the rectangle in everything."
Van Gogh: "Dashes stream around your mark like water around a rock."
Footer: "You don't study the technique. You have a conversation in it."

**Card 6, How it works.** Title "Look. Understand. Answer. Draw." with the subtitle "Viam under every step." Four nodes in a row joined by arrows:
Look: "Viam camera component. RealSense colour and depth, aligned, from the wrist. The board is found again every turn."
Understand: "Claude Opus 5. One photo in, two sentences and strokes out."
Answer: "The artist's grammar styles the strokes. The planner clips and budgets them, in board millimetres mapped into Viam's world frame."
Draw: "Viam motion service. Every move planned around the table and wall obstacles, linear constraints on pen-down, arm and gripper components over the Python SDK."
A strip along the bottom: "viam-server owns the arm's control box · machine configured in app.viam.com · Python SDK from a laptop · motion service with obstacles · camera, arm, gripper components."
Four numbers in a row: "8 s to look and decide" · "2 mm calibration" · "120 tests" · "0 direct arm moves".
The test count is confirmed against the suite on the day before the deck is final; if it differs, the slide changes, not the claim.

**Card 7, The build.** "One person. Two days. Claude and Viam." Then "Nicholas Fjellberg Swerdlowe · Viam Fine Motor Skills Hackathon · September 2026". Footer, larger than a footer usually is: "Draw one mark. Duet answers." This card stays on screen while the demo runs.

## 3. Look

Bright Haring plates. Every card is a saturated colour plate covered edge to edge in a repeating hand-drawn pattern in Keith Haring's style, with bold black type on top. The deck borrows Haring's grammar, not his drawings: no reproductions of his figures, only the kinds of marks he used.

- **Stage.** The same 16:9 stage as the live page, letterboxed in black in any window (`width: min(100vw, 177.78vh)`, `aspect-ratio: 16/9`). Inside it, the plate fills the whole card.
- **Plates, one colour per card.** 1 Thesis: yellow. 2 What Duet is: red. 3 One turn: blue. 4 Co-creation: green. 5 Learning: orange. 6 How it works: cream (a light plate so the diagram reads). 7 The build: black with the pattern in all the bright colours at once, white type. Tokens: yellow `#ffd400`, red `#e5322d`, blue `#1f4fd6`, green `#17a34a`, orange `#ff7a00`, cream `#fff4d6`, ink `#111`, paper `#fff`. The page's `#1b8f3a` green and `#c62828` red still mark the robot's ink and the visitor's ink where the copy refers to them.
- **Plates.** Each card's background is a generated 16:9 texture, `img/plate-N.jpg`: hand-drawn black marks on white (wavy squiggles, zigzags, radiating tick clusters, dots, open arcs, plus one small extra motif per card) spread evenly edge to edge. It is laid over the CSS plate colour with `mix-blend-mode: multiply` at 14 percent opacity (10 percent on cream), so the colour stays exact and the marks read as ink; card 7's texture is the five bright colours on black at full opacity. A very slow 4 percent zoom over 30 seconds, alternating, gives the plate life; it stops under `prefers-reduced-motion`. The inline SVG `<pattern>` tile (about 160 px, the same motifs, drifting one period) sits under the image and is hidden once the image has loaded. Neither layer sits behind a photo, a hero, or a speech bubble.
- **Heroes.** Three generated square illustrations on white, each on a paper card: card 1, a figure holding an open book and a marker with ticks around the head; card 2, a person and a six-jointed robot arm drawing on the same board with one loopy line joining their marks; card 7, a figure dancing beside the arm. Thick uniform black outlines, flat colour, no text. Cards 1, 2 and 7 become two columns, words left and hero right.
- **Type.** Fredoka from a local font file in `fonts/`, falling back to Chalkboard SE, Comic Sans MS, then sans-serif. Headlines heavy (600 to 700), black, large; the one word that matters on each card is set in white with a black outline (a Haring-style keyline via `paint-order: stroke` or a text shadow stack) rather than in a second colour. Sizes scale with the stage using container units.
- **Paper.** Photos, the speech bubble, the artist chips, the four numbers on card 6, and the diagram nodes sit on white paper cards with a thick black outline (about 4 px at full size) and rounded corners, the way Haring's figures are outlined. No soft shadows; the outline does the work.
- **Artist chips.** Inline SVG paths, no images: a swirl of short dashes (Van Gogh, blue), a small grid with one red hatched cell (Mondrian, blue lines), a bold outline with ticks (Haring, green). Each on its own paper card.
- **Flipbook.** One `<img>` on a paper card whose `src` a timer swaps; all 13 images are preloaded when the deck opens so the first loop is smooth.
- **Motion.** The card-1 line reveals (a short fade and rise), the pattern drift, the flipbook, and a short cross-fade between cards. Nothing bounces.

## 4. Controls

| Input | Action |
| --- | --- |
| Right arrow, space, click on the right two thirds of the stage | Advance: on card 1, reveal the next line; otherwise next card |
| Left arrow, click on the left third | Back: on card 1 with lines revealed, hide the most recent line; otherwise go to the previous card fully revealed |
| 1 to 7 | Jump to that card |
| Home, End | First card, last card |
| F | Toggle fullscreen |
| D | Toggle developer mode (see below) |

- The URL hash mirrors the card (`#3`), so a refresh keeps the place and a link can open on a card.
- A faint "3 / 7" sits bottom right, low contrast, small.
- No presenter notes view. Nicholas rehearses from this spec.

**Developer mode** follows `~/.claude/rules/common/preview-dev-mode.md`: every meaningful element carries a specific `data-el` name (for example `data-el="card 3 speech bubble — sees"`, `data-el="card 4 flipbook image"`, `data-el="card 6 node — Draw"`); D toggles a badge, hover shows the name, click copies it and shows a toast, and clicks in dev mode do not advance the deck. Key handling ignores keystrokes typed into inputs, of which the deck has none.

## 5. Files

```
docs/duet/pitch/
  index.html        the seven cards, the SVG motifs and patterns, the artist symbols, the developer-mode elements
  deck.css          plates, pattern, type, paper, chips, bubble, flipbook, counter, developer-mode styles
  fredoka.css       @font-face with Fredoka (variable 400 to 700, latin) as a base64 data URI
  deck.js           window.Deck state functions, then DOM wiring guarded by typeof document
  dev.js            the D-key developer mode
  gen_images.py     the Nano Banana 2 generator (prompts, one call per missing image, JPEG via sips)
  README.md         how to open it and the keys
  img/turn-00-start.jpg ... img/turn-06-robot.jpg   the 13 photos, copied unchanged (704 x 960)
  img/plate-1.jpg ... img/plate-7.jpg             generated plate textures, 2K 16:9
  img/hero-thesis.jpg, img/hero-duet.jpg, img/hero-build.jpg   generated heroes, 2K square
```

Amended 2026-09-19 while planning and building: Chrome, the default browser on the presenting Mac, blocks web fonts and module scripts loaded over file:// under its CORS rules. So the font is embedded as a data URI in its own stylesheet, the script is a classic script, and its pure state functions are exposed on window.Deck so Node can test them without a DOM. The photos are already 704 x 960 and are copied, not downscaled. Card 7's words sit on a black panel because bare type over the full-colour plate failed the legibility check.

- The photos are copies of `code/hackathon/sessions/20260918-190258/turn-*.jpg`, downscaled with a one-line script or `sips` so the deck stays a few megabytes and opens instantly from disk. Originals are untouched.
- The font is fetched once while online and committed; without it the fallback stack renders, which is acceptable but not the plan.
- No API keys, machine credentials, or session JSON are copied into the deck folder. Claude's two sentences are typed into the HTML. The Gemini key lives only in `code/hackathon/.env` as `GEMINI_API_KEY`; `gen_images.py` reads it from there and sends it in a header, never in a URL or a tracked file.
- Opening the deck: `open docs/duet/pitch/index.html`. No server is needed; every reference is relative and works over `file://`.

## 6. Verification

- **Node test** `code/hackathon/pagetests/pitch.test.mjs`, run with the existing `node --test 'pagetests/*.test.mjs'`: reads `docs/duet/pitch/index.html`, asserts seven cards in order with the expected headline text, asserts every `src`, `href` and `url()` that points into `img/` or `fonts/` names a file that exists, asserts the 13 flipbook filenames are listed, asserts the seven plates and three heroes are referenced and exist, asserts `gen_images.py` never names the artist, and asserts the developer-mode badge, label, and toast elements are present.
- **Browser pass** with the built-in browser: open the file, step through all seven cards with the keyboard, take one screenshot per card into `code/hackathon/captures/pitch-N.png`, confirm the card-1 reveals, the flipbook cycling, the hash updating, fullscreen, and developer mode copying a name. Screenshots are shown to Nicholas for review before 3:30.
- **Legibility check** during the browser pass: on each plate, the headline and body type are read at arm's length from a laptop and at the back of a room from a projector-sized window; if the pattern competes with the type, its opacity comes down, never the type size.
- **Offline check**: the browser pass is repeated once with the network off (or with Google Fonts blocked) to confirm the local font loads and nothing else is fetched.

## 7. Out of scope

- Speaker notes, timers, or a presenter view.
- Video embeds, audio, or the session's stitched `session.mp4` (the flipbook covers it).
- A public URL. The deck is opened from disk on the presenting laptop.
- Any change under `code/hackathon/duet/`. The deck does not touch the running app.

## 8. Git

Built and committed on `feat/duet-design`, the branch the demo runs from, in small commits: the spec, the assets, the deck, the test. Nothing under `duet/` is staged.

## 9. Notes for the web (added 2026-09-20)

The deck now lives on the showcase site, where nobody hears the talk. Each card gained an aside that takes an
implicit fourth grid row under the content, holding a paper speech bubble with a technical product manager's
walkthrough of the slide (the context, what is happening technically, who the user is, the feature), written in the
present tense of the day: the deck is a snapshot of the pitch as given, and it still sells. `N`, the Notes pill, and
`?notes=0` hide the bubbles, which restores the room version. The stage flag is `shownotes`, not `notes`, so the
asides' own hide rule cannot match the stage. With the notes on, the type comes down a step (`--headline` 4.1cqw and
`--body` 2.5cqw hold the fit; `--display` and `--caption` follow for the scale) and the fixed-height pictures
shrink, so every card fits its plate from phone-landscape to 1920 wide. Card 3 names the speaker ("Claude says") and
rounds the badge to "about 8 seconds". Card 5 marks "Your own artist" as "Coming next". Card 7 dropped the rig
instruction for "Next: artists you train yourself" and a Play the demo pill; its bubble carries the diner story and
the wish to train Duet on a family member's hand. Plan: `docs/superpowers/plans/2026-09-20-deck-notes.md`.
