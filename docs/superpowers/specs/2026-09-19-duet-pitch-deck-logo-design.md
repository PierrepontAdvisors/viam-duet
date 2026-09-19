# Duet pitch deck: frame wash and toy logo

Date: 2026-09-19, early afternoon. Status: approved in brainstorming (visual companion), ready for the plan below.
Extends `docs/superpowers/specs/2026-09-19-duet-pitch-deck-grid-design.md`. Everything not named here is unchanged.

## 1. Decisions

- **The inside of the frame is calmer than the margin.** A translucent wash covers the area inside the frame on every card: white at 22 percent on the colour plates (12 percent on cream), black at 35 percent on card 7. The plate texture keeps its opacity; the wash lifts the ground under the type. The margin outside the frame keeps the full plate colour, so the frame now reads as a mat.
- **The Duet logo is a row of four toy alphabet blocks**, D U E T, one per block, in yellow, red, blue and green, each tumbled a few degrees, thick ink keyline, with a marker squiggle underneath. Vector, drawn once as an SVG `<symbol id="logo">` with Fredoka text, ink parts in `currentColor` so it turns white on card 7. Nicholas chose it over fridge-magnet letters and balloon letters.
- **Where the logo goes (option C):** top-right in the header band on every card, in place of the word "Duet"; bottom-left in the footer band in place of "Viam Fine Motor Skills · 2026" on cards 1 to 5 and 7; large on card 2 in place of the display-size "Duet". Card 6's footer keeps the Viam strip, which is content, and has no footer logo.

## 2. Sizes

Header logo height 3.2cqw; footer logo height 2.4cqw; card 2 logo width 20cqw (about 8cqw tall; every `<svg class="logo">` use carries `viewBox="0 0 320 130"`, without which the browser sizes the box at 300 by 150 pixels and the logo floats inside it), so card 2's words column still fits: logo, subtitle, beats, chips with 2cqw gaps come to about 38cqw of the 39 available.

## 3. Files and tests

- `index.html`: the symbol in `<svg class="defs">`; `.wordmark` spans wrap `<svg class="logo"><use href="#logo"/></svg>` with `role="img"` and `aria-label="Duet"`; footers of cards 1 to 5 and 7 replace the `.strip` text with the same svg (class `logo foot-logo`); card 2's `h1.name` holds the large logo instead of text. Every card gains a `<div class="wash">` between the plate image and the frame. `data-el` names stay; the footer logo carries "card N footer logo".
- `deck.css`: `.wash`, `.plate-black .wash`, `.plate-cream .wash`, `.logo { color: var(--ink) }`, `.plate-black .logo { color: #fff }`, and the three sizes.
- `pagetests/pitch.test.mjs`: a new test asserts the symbol has four blocks with D, U, E, T; every card has one header logo inside `.wordmark`; cards 1 to 5 and 7 have a footer logo and no "Viam Fine Motor Skills" text; card 6's footer keeps the strip; each card has a wash; the CSS has `.wash` and `.plate-black .wash`. The existing tests keep passing (the copy list does not include the footer line).
- Verification: Node suite green; headless Chrome renders of cards 1, 2, 6 and 7 at 1280 by 720 checked for the wash, the logo at all three sizes, and card 2's fit.
