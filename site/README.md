# Duet showcase site

A static site for the hackathon build: a homepage, the pitch deck as the presentation, and the live page
replaying the longest recorded session as the demo. Spec: `docs/superpowers/specs/2026-09-20-duet-showcase-site-design.md`.

```
index.html, home.css     the homepage (hand-written)
assets/                  tokens and the embedded Fredoka, copied from the page
presentation/            docs/duet/pitch, copied, with a Home link beside the playbar
demo/                    code/hackathon/duet/static in replay mode, plus replay.json and the session's files
vercel.json              clean URLs, long cache on the photos
build.py                 assembles assets/, presentation/, demo/ from the sources
```

## Rebuild

After changing the page, the deck, or the recording:

```
python3 site/build.py                             # the session with the most turns under code/hackathon/sessions (gitignored recordings)
python3 site/build.py --session 20260919-151119   # a specific one
python3 site/build.py --sessions site/demo/sessions --session 20260919-151119   # a fresh clone: from the session that ships in demo/
```

Run it with the hackathon venv's Python (`code/hackathon/.venv/bin/python`) so the visitor's marks are traced from the photos with OpenCV as the live page does; plain `python3` falls back to the plan files' traced ink and the demo's hand draws less.

Standard library only. Commit the result: Vercel serves the folder as it is, with no build step.

## Try it locally

```
python3 -m http.server 8090 -d site
```

Then http://localhost:8090/ for the homepage, `/presentation/` and `/demo/`. Add `?speed=3` to the demo to
watch it faster; Go skips the visitor's turn; Start on a finished piece plays it again.

## Deploy

The Vercel project `viam-duet` is linked to the GitHub repository with Root Directory `site` and no build step, so every push to `main` deploys production at https://viam-duet.vercel.app. A manual deploy from a checkout:

```
cd site && vercel --prod
```

or import the repository in the Vercel dashboard with Root Directory `site` and no build command.
