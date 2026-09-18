#!/usr/bin/env bash
# Re-download the Viam docs mirror. Every page on docs.viam.com is also served as Markdown
# (drop the trailing slash, add .md). Run from the repo root: bash docs/viam/refresh.sh
set -euo pipefail
cd "$(dirname "$0")"
curl -sSL -o sitetree.json https://docs.viam.com/sitetree.json
curl -sSL -o llms.txt https://docs.viam.com/llms.txt
curl -sSL -o llms-full.txt https://docs.viam.com/llms-full.txt
mkdir -p tutorials/services && curl -sSL -o tutorials/catalog.md https://docs.viam.com/tutorials/catalog.md
# tutorials are hidden from the site tree; keep the ones that match the hackathon hardware
curl -sSfL -o tutorials/pick-and-place.md https://docs.viam.com/tutorials/pick-and-place.md
curl -sSfL -o tutorials/services/plan-motion-with-arm-gripper.md https://docs.viam.com/tutorials/services/plan-motion-with-arm-gripper.md
for p in platform-mental-model configure-resources static-positions control-the-robot-from-python perception-guided-picking inline-module wrap-up; do
  mkdir -p tutorials/pick-and-place
  curl -sSfL -o "tutorials/pick-and-place/$p.md" "https://docs.viam.com/tutorials/pick-and-place/$p.md"
done
python3 - <<'PY' > /tmp/viam-doc-urls.txt
import json
def walk(n):
    if isinstance(n, dict):
        if 'path' in n: yield n['path']
        for c in n.get('children', []): yield from walk(c)
    elif isinstance(n, list):
        for c in n: yield from walk(c)
for p in walk(json.load(open('sitetree.json'))):
    rel = p.replace('https://docs.viam.com/', '').rstrip('/')
    out = (rel + '.md') if rel else 'index.md'
    url = 'https://docs.viam.com/index.md' if not rel else f"{p.rstrip('/')}.md"
    print(f"{url}\t{out}")
PY
while IFS=$'\t' read -r url out; do
  mkdir -p "$(dirname "$out")"
  printf '%s\t%s\n' "$url" "$out"
done < /tmp/viam-doc-urls.txt | xargs -P 6 -L 1 bash -c 'curl -sSfL -o "$1" "$0" || echo "FAILED $0"'
date -u +"downloaded %Y-%m-%dT%H:%M:%SZ" > LAST_REFRESH
echo "done: $(find . -name '*.md' | wc -l) markdown files"
