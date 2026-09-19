# Duet pitch deck: step icons, your-own-artist module, entrance motion

Date: 2026-09-19, about 12:45. Status: built from Nicholas's change list; two choices he had not answered are recorded as assumptions.
Extends the grid spec and the logo spec. Everything not named here is unchanged.

## 1. Card 6, How it works

- Each step is a `.step`: a paper box (icon beside the name, one simple sentence at body size) and, under the box, a Viam line at caption size that says what Viam does at that step.
- Icons, one per step, drawn as SVG symbols in the deck's grammar (thick round ink strokes, one plate colour each): `i-look` an eye with ticks (blue), `i-think` a thought cloud (yellow), `i-answer` a marker mid-squiggle (green), `i-draw` a three-joint arm (red).
- Copy. Look: "The camera on the wrist photographs the board." / "Viam · the camera component streams colour and depth from the wrist." Understand: "Claude reads the drawing and decides what to add." / "Viam · the frame reaches Claude through the Python SDK." Answer: "The artist's style turns that idea into strokes." / "Viam · board millimetres map into the machine's world frame." Draw: "The arm draws them, planned safely around the table." / "Viam · the motion service plans every move around the table and wall."
- Removed: the four numbers row and the footer strip. Card 6's footer is the name line like every other card. Assumption: "the technical information at the bottom" covers both, since the Viam lines now carry the proof.

## 2. Card 5, Learning

- Four modules at three columns each. The three artists keep their drawings and lessons; the module head becomes a row (drawing or icon beside the name) so four fit.
- The fourth, "Your own artist": the `i-own` pencil-and-sparkle icon (orange), a "Next" pill in the head, a prompt example as a pill, "Bold comic-book lines with halftone dots", and the line "Describe a style in one sentence. Duet answers in it." Assumption: the "Next" pill stays because the feature is not built; the app has three styles.

## 3. Motion

- When a card becomes active, everything inside the frame enters in reading order with a toy pop: from 92 percent scale and 1cqw low, overshooting to 102 percent, settling in 450 ms; each element 80 ms after the previous: kicker, logo, then the content blocks (words children or modules or triptych modules), then the footer. Card 1's three lines keep their key-driven reveal and are excluded from the pop. The frame, plate and wash stay still.
- Assumption: toy pop (option B) over quiet rise.
- `prefers-reduced-motion: reduce` turns every entrance animation off.

## 4. Tests

The copy test drops the old node copy and strip and gains the new sentences, the Viam lines and the fourth module's text. The master-page and logo tests no longer special-case card 6. A new test asserts the five icon symbols exist and are used, card 5 has four modules, card 6 has four Viam lines, and the CSS has `@keyframes pop` with the reduced-motion guard.
