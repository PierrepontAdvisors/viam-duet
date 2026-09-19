# Duet pitch deck

Seven cards, about two minutes, then the live demo. Spec: `docs/superpowers/specs/2026-09-19-duet-pitch-deck-design.md`.

Open it (offline is fine; the font is embedded):

    open docs/duet/pitch/index.html

Keys: Right, space, or a click on the right two thirds advances; Left or a click on the left third goes back;
1 to 7 jump; Home and End; F fullscreen; D developer mode (hover shows an element's name, click copies it).
Card 1 reveals three lines before it advances. Card 7 stays on screen during the demo.

Images: `python3 docs/duet/pitch/gen_images.py` regenerates any missing plate or hero with Nano Banana 2
(`GEMINI_API_KEY` in `code/hackathon/.env`); `--force <name>` re-rolls one.

Checks: `cd code/hackathon && node --test 'pagetests/*.test.mjs'`
