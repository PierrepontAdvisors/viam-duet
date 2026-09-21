# Duet pitch deck

Seven cards, about two minutes, then the live demo. Spec: `docs/superpowers/specs/2026-09-19-duet-pitch-deck-design.md`.

Open it (offline is fine; the font is embedded):

    open docs/duet/pitch/index.html

Keys: Right, space, or a click on the right two thirds advances; Left or a click on the left third goes back;
1 to 7 jump; Home and End; F fullscreen; N toggles the notes; D developer mode (hover shows an element's name, click copies it).
P, or the Play pill at the bottom right, loops the deck on its own (every reveal, then every card, 6 s a card at 1x,
12 s on the flipbook); the Speed dropdown runs it at 0.5x to 2x and paces the pop-in of each object to match.
Card 1 reveals three lines before it advances. Card 7 stays on screen during the demo.

Notes: each card carries the spoken part of the pitch in a speech bubble, for readers who were not in the room.
N or the Notes pill toggles them (the pill reads Notes on or Notes off); `?notes=0` opens with them hidden. Card 7 links to `../demo/` and the corner
links to `../`, which resolve on the showcase site (`site/`), not from this folder.

Images: `python3 docs/duet/pitch/gen_images.py` regenerates any missing plate or hero with Nano Banana 2
(`GEMINI_API_KEY` in `code/hackathon/.env`); `--force <name>` re-rolls one.

Checks: `cd code/hackathon && node --test 'pagetests/*.test.mjs'`
