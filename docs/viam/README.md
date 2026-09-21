# Viam docs mirror

Local Markdown copy of https://docs.viam.com, one file per page, same paths as the site
(`reference/components/arm.md` mirrors `https://docs.viam.com/reference/components/arm/`).

- Source: docs.viam.com. Viam publishes the docs under the Creative Commons Attribution-ShareAlike 4.0 license (CC BY-SA 4.0; see https://github.com/viamrobotics/docs/blob/main/LICENSE). This mirror redistributes them unchanged under that same license.
- Refresh: `bash docs/viam/refresh.sh` from the repo root. Date of the last refresh is in `LAST_REFRESH`.
- `llms.txt` is the site's own index for AI agents; `llms-full.txt` concatenates the agent-first pages.
- `sitetree.json` is the navigation tree the refresh script walks.
- Search it with `grep -ril "<term>" docs/viam`.
