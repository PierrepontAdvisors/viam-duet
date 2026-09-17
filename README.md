# Viam 101 — Course Notes

Personal notes and exercise code for the Viam 101 workshop (cohort `palletizer-101`).
The course builds a palletizing robot in simulation using Viam's motion and vision services and the Python SDK. No hardware is required.

- Course: https://viam-101-w28-9jnk.learn.viam.com/workshop/content/print.html (requires login)
- Viam docs: https://docs.viam.com
- Viam app: https://app.viam.com

## Layout

| Path | What goes there |
|------|-----------------|
| `notes/00-course-overview.md` | The course outline and how far along I am |
| `notes/01-setup.md` | Environment setup: viam-server, CLI, SDK, app.viam.com |
| `notes/modules/` | One file per course module, copied from `_TEMPLATE.md` |
| `notes/glossary.md` | Viam terms in my own words |
| `notes/stuck-log.md` | Every problem I hit, what fixed it, and why |
| `notes/questions.md` | Open questions for instructors or Claude |
| `code/` | Exercise code, one folder per module |
| `resources.md` | Links worth keeping |

## Conventions

- Start a new module: copy `notes/modules/_TEMPLATE.md` to `notes/modules/NN-short-name.md`.
- Log a problem in `notes/stuck-log.md` before fixing it. The fix is the useful part, so come back and fill it in.
- Never commit API keys, robot secrets, or machine configs containing credentials. `.gitignore` covers the obvious files, but check `git diff` before committing.
