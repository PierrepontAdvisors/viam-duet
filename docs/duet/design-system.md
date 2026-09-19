# Duet design system

One page for anyone touching the deck or the live page. Written 2026-09-19 at the Viam Fine Motor Skills hackathon.

## Where it lives

| What | File | Notes |
| --- | --- | --- |
| Tokens (source of truth) | `code/hackathon/duet/static/tokens.css` | colours, type, space, paper, frame, the `pop` keyframe |
| Live page styles | `code/hackathon/duet/static/duet.css` | uses the tokens; owns stage, chips, bubbles, panel |
| Deck styles | `docs/duet/pitch/deck.css` | mirrors the tokens in its own `:root` so the deck stays a self-contained folder; change both when a token changes |
| Font | `code/hackathon/duet/static/fredoka.css`, `docs/duet/pitch/fredoka.css` | Fredoka variable 400 to 700 embedded as a data URI, so nothing loads from the network |
| Logo and icons | `<symbol id="logo">` in both `index.html` files; step icons `i-look`, `i-think`, `i-answer`, `i-draw`, `i-own` in the deck | ink parts in `currentColor` |

Every size is in `cqw`, one percent of the 16:9 stage's width, so the same numbers hold on a laptop and a projector.

## Tokens

- **Colour.** Plates: yellow `#ffd400`, red `#e5322d`, blue `#1f4fd6`, green `#17a34a`, orange `#ff7a00`, cream `#fff4d6`. Ink `#111`, paper `#fff`. The robot's ink on the board stays `#1b8f3a` and the visitor's `#c62828`; those are marker colours, not UI colours.
- **Type.** Fredoka, falling back to Chalkboard SE and Comic Sans MS. Four sizes only: display 6.4, headline 4, body 2.1, caption 1.3 cqw. Weights 700 for display, headline and captions, 600 for body. Headlines and body use `text-wrap: balance`.
- **Space.** 1, 2, 3, 4 cqw. Nothing in between.
- **Paper.** White, ink border .35cqw, radius 1.2cqw, padding 1.6cqw. Every card-like thing is paper: chips, pills, photos, heroes, nodes, bubbles.
- **Frame.** Ink keyline .45cqw, inset 3cqw on the deck; on the live page the keyline hugs the camera stage, which sits at 93 percent of a 16:9 mat.
- **Grid.** 12 columns, gutter 1.2cqw, content padding 8cqw sides and 4.5cqw top and bottom on the deck.

## Master page (deck)

Plate colour with the squiggle texture (generated plates at 12 percent, SVG tile as fallback) and a wash inside the frame (white 22 percent, cream 12, black card 35 percent black). Header band: kicker pill top-left ("03 · One turn"), logo top-right. Footer band: name and event left, counter right. Content on the grid between them in one of three templates: split (words 1–7, figure 9–12), triptych (three modules of four columns), modules (headline across, equal modules under it).

## Components

- **Kicker pill.** Caption size, 700, uppercase, letter-spacing .12em, paper with the ink border, fully rounded.
- **Pill.** Same as the kicker without uppercase; `yellow` for the active state, `red` with white text for danger.
- **Chip (live page).** A pill at 1.6cqw with tones `green` (your turn), `red` (robot's turn, paused), `yellow`, `white`, `black` (paper).
- **Speech bubble.** Yellow paper with a right or left ink tail; **thought bubble** white paper with two dots; the thinking pulse scales 4 percent.
- **Logo.** Four toy blocks D U E T in yellow, red, blue, green with a marker squiggle; header height 3.2cqw; 20cqw wide on the deck's card 2. Ink parts follow `currentColor`, so it turns white on black.
- **Step icons.** Eye with ticks, thought cloud, marker mid-squiggle, three-joint arm, pencil and sparkle. Thick round ink strokes, one plate colour each.
- **Panel (live page).** Paper at 94 percent over the picture, ink top rule, Fredoka labels, pill buttons.
- **Buttons, the toy press.** Every button rests on a hard ink shadow (.18cqw in the panel, .25 on chips, .4 on Start and Go). Hover lifts it a step and tilts it one degree while the shadow grows; press squashes it onto its shadow; a panel switch that is on sits pressed in yellow. Disabled buttons do not move. Start and Go wiggle once (three degrees, 600 ms) after they pop in.
- **Welcome page (live page).** The zero state: logo, "A robot arm that draws with you.", two lines, Start. Shows at load, when a fresh session begins, and 8 seconds after a session ends. Start hides it; on a finished session it sends `restart` and waits.

## Motion

One entrance, `pop`: from 92 percent scale and 1cqw low, overshooting to 102 percent, settling in 450 ms. The deck staggers it 80 ms per element in reading order when a card becomes active; the live page fires it on the state pill, the count pill, the bubble and the Go button when their content changes. Plates breathe or drift slowly. `prefers-reduced-motion` turns all of it off.

## Rules

- Add a size only by adding a token; the deck's tests fail on any `font-size` that is not one of the four.
- Prompts for generated images describe marks, never an artist's name.
- Never stage `.env`; the Gemini key for the generator lives there.
