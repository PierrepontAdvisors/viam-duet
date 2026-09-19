# Duet pitch deck: grid and design system

Date: 2026-09-19, early afternoon. Status: approved in brainstorming (visual companion storyboard), ready for an implementation plan.
Extends `docs/superpowers/specs/2026-09-19-duet-pitch-deck-design.md`. Copy, images, controls, developer mode, files and tests from that spec stand unless this document says otherwise.

## 1. Purpose

The first build placed each card's content by feel: nothing repeated from card to card, edges never lined up, nine type sizes, chips and paper cards of different sizes. This document puts every card on one master page and one 12-column grid, with four type sizes, one spacing scale and one paper style, so the deck reads as a designed system. Nicholas chose the poster-frame master page over header bands and an open grid, and approved the seven-card storyboard as drawn.

## 2. Master page (every card)

- **Frame.** A keyline inset 3cqw from the stage edge on all sides, .45cqw thick, radius 1.2cqw, ink black; white on card 7. Content never touches it.
- **Header band.** Inside the frame, a kicker pill top-left and the wordmark top-right. Kicker: caption size, 700, uppercase, letter-spacing .12em, white paper pill with the ink border, text "01 · Thesis", "02 · What Duet is", "03 · One turn", "04 · Co-creation", "05 · Learning", "06 · How it works", "07 · The build". Wordmark: "Duet" at headline size, 700, ink (white on card 7).
- **Footer band.** Inside the frame, caption size, 600: left "Viam Fine Motor Skills · 2026", right the counter "N / 7". On card 6 the left text is the Viam strip instead: "viam-server owns the arm's control box · machine configured in app.viam.com · Python SDK from a laptop · motion service with obstacles · camera, arm, gripper components".
- **Content area.** Between the bands, on the grid below. Vertical centring of the content within the area is the default; cards 5 and 6 fill it top to bottom.
- The single stage-level counter is replaced by the per-card footer counter; `deck.js` writes the same "N / 7" into every `.counter` element.

## 3. Tokens

| Token | Value | Use |
| --- | --- | --- |
| Grid | 12 columns, gutter 1.2cqw, content padding 5cqw top and bottom, 8cqw sides | every card |
| Display | 6.4cqw / 1.05, weight 700 | card 1 lines, card 2 wordmark, card 7 headline |
| Headline | 4.0cqw / 1.1, weight 700 | card 2 subtitle, card 4 headline, card 5 headline, card 6 title, page wordmark |
| Body | 2.1cqw / 1.3, weight 600 | beats, bubble sentences, lessons, node text, card 4 line, credit |
| Caption | 1.3cqw / 1.2, weight 700 (600 in footers) | kicker, footer, chip labels, photo captions, number labels, badge, flip counter |
| Space | 1, 2, 3, 4 cqw | gaps and paddings, nothing in between |
| Paper | radius 1.2cqw, border .35cqw ink, padding 1.6cqw, white | chips, photos, heroes, nodes, numbers, bubble |
| Plate pattern | image at 12 percent, cream 8 percent, black plate 35 percent, `mix-blend-mode: multiply` (normal on black) | all cards; SVG pattern stays as the fallback |
| Key word | white with .05em ink keyline (yellow on card 7) | one word per card, unchanged |
| Colours | plates as before; ink `#111`; paper `#fff`; robot green `#1b8f3a` for the "adds" sentence | unchanged |

Type sizes outside these four are not used. Card 7 no longer needs the black panel behind its words because the plate drops to 35 percent; the panel is removed.

## 4. Templates and the seven cards

Three templates on the grid. Columns are numbered 1 to 12; "cols a–b" means grid lines a to b+1.

**Split**: words in cols 1–7, figure in cols 9–12 (a square paper card holding the hero, or the portrait flipbook), both vertically centred in the content area.
- Card 1, Thesis: three display lines stacked with space 3 between; the reveal per advance stays. Hero `hero-thesis.jpg`.
- Card 2, What Duet is: wordmark (display), subtitle (headline, one line at 1280 wide: "A robot arm that draws with you."), three beats (body) stacked with space 1, then the three chips in a row spanning exactly cols 1–7 with gutter gaps. Hero `hero-duet.jpg`.
- Card 4, Co-creation: headline, then the line (body) with space 2. Figure: the flipbook photo on paper, its counter pill centred under it (caption).
- Card 7, The build: headline (display; "One person." in yellow keyline), credit (body, 85 percent opacity), then "Draw one mark. Duet answers." (headline, yellow) with space 3 above it. Hero `hero-build.jpg`. White frame, white wordmark and footer.

**Triptych** (card 3, One turn): three modules of cols 1–4, 5–8, 9–12, vertically centred. Left and right: the portrait photo on paper, height 34cqw, with its caption under the card ("Your mark", "Duet answers", caption size, white). Middle: the speech bubble as a squared paper card filled yellow, padding 2cqw, radius and border from the paper token, with a small ink tail on its right edge pointing at "Duet answers"; the two sentences at body size (the "adds" sentence in robot green), the "8 s to look and decide" badge (caption pill) under them.

**Modules** (cards 5 and 6): headline across cols 1–12 at the top of the content area, then equal paper modules under it, then a closing line.
- Card 5, Learning: three modules of four columns, each a paper card with the artist chip drawing at the top (the SVG sample at 9 by 5.4cqw), the artist name (caption) and the lesson (body). Closing line "You don't study the technique. You have a conversation in it." at body weight 700.
- Card 6, How it works: title (headline) and subtitle (body, "Viam under every step." with the keyline) at the top; four node modules of three columns (name at body 700, text at caption size 600, line-height 1.3); under them, in the same four columns, the four number cards (number at headline size, label at caption); no arrows. The Viam strip moves to the footer band.

## 5. Files and tests

- `deck.css` is rewritten around the tokens as custom properties (`--display`, `--headline`, `--body`, `--caption`, `--s1` to `--s4`, `--paper-radius`, `--paper-border`, `--paper-pad`, `--gutter`) and the three template classes `.split`, `.triptych`, `.modules`; per-card rules only place things on the grid.
- `index.html` keeps the same copy, images, `data-el` names and card ids; each card gains a header band (`.kicker`, `.wordmark`), a `.content` on the grid, and a footer band (`.foot`, `.counter`). New elements carry `data-el` names ("card 3 kicker", "card 3 footer", "card 3 wordmark").
- `deck.js`: `render` updates every `.counter`; nothing else changes. The pure functions and their tests are untouched.
- `pagetests/pitch.test.mjs`: the copy test keeps every line; a new test asserts each card has one kicker with the right text, one wordmark, one footer with a counter, and that card 6's footer carries the Viam strip; the CSS test asserts the token custom properties and the three template classes exist and that no `font-size` outside the four tokens remains (a regex over `font-size:` values allows only `var(--display|--headline|--body|--caption)`).
- Verification: the Node suite green; headless Chrome screenshots of all seven cards over `file://` at 1280 by 720 into `code/hackathon/captures/pitch-N.png` (ignored by git), reviewed for alignment (hero top edge level with the text block's top, chips spanning the text column, node and number columns coincident) and legibility.

## 6. Out of scope

New copy, new images, new cards, animation beyond the existing reveal and slow plate motion, and any change under `code/hackathon/duet/`.
