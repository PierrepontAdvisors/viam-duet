# Duet repository

Duet is a robot arm that draws with you, built at Viam's Fine Motor Skills hackathon (September 2026). The repo holds the app (`code/hackathon`), its design record (`docs/duet`, `docs/superpowers`), the showcase site (`site`), and the notes the repo began as (`notes`, from Viam's 101 workshop). The README explains how the pieces fit and how to run them.

- Never write API keys, machine addresses, or credentials into any tracked file. They belong only in `code/hackathon/.env`, which is gitignored; `.env.example` lists the keys.
- Each piece of the build has a design spec in `docs/superpowers/specs` and a plan in `docs/superpowers/plans`. Add to those when changing behaviour, and keep the tests beside the code: `pytest` under `code/hackathon/tests`, Node's test runner under `code/hackathon/pagetests`.
- The showcase site is generated and committed: after changing the page or the deck, run `code/hackathon/.venv/bin/python site/build.py --sessions site/demo/sessions --session 20260919-151119` from the repository root (the venv, for OpenCV) and commit the result. Bump the `?v=` tag on the page's assets when its scripts or styles change.
- `docs/viam` is a mirror of Viam's documentation (CC BY-SA 4.0); search it, do not edit it by hand.
- `notes/` is personal course material. Keep edits there light-touch; do not reformat or "improve" existing notes unless asked.

<!-- git-safety-guardrail -->
## Git safety

- Never commit or push directly to `main`. Work on a feature branch and open a PR.
- Commit early and often; never force-push; never discard uncommitted work with reset --hard / clean -f.
- Enforced globally by ~/.claude/hooks/git-safety-guard.js and by GitHub branch protection.
