"""Generate the class deck's story pictures with Nano Banana 2, in the pitch deck's cartoon grammar.

Reuses the pitch's generator (docs/duet/pitch/gen_images.py) for the endpoint, the key lookup and the JPEG
conversion; only the jobs live here. GEMINI_API_KEY in the environment wins over code/hackathon/.env. Writes into img/ beside this file, skips images that exist unless
--force is given. The text-only cards (4, 9, 10, 11, 12, 14) each get a picture, or a strip of them, and
the words move under the pictures.

    python3 docs/duet/class/gen_images.py                 # everything missing
    python3 docs/duet/class/gen_images.py story-9         # one image
    python3 docs/duet/class/gen_images.py --force story-4-2
"""
import importlib.util
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"
SIZE = "1K"                                        # panels are at most a third of the card wide

spec = importlib.util.spec_from_file_location("pitch_gen", HERE.parent / "pitch" / "gen_images.py")
pitch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pitch)
GRAMMAR = pitch.GRAMMAR

KID = "a small simple outlined kid"
DAD = "a tall simple outlined grown-up"
ARM = "a simple outlined six-jointed robot arm"

STORIES = {
    # card 4, the diner: one panel per line, revealed with it
    "story-4-1": (f"{DAD} sitting in a diner booth, an architect: a fat marker tucked behind one ear, a rolled-up "
                  "drawing under one arm, a mug of coffee on the table. Blue grown-up, pure white background. ", "1:1"),
    "story-4-2": (f"{DAD} and {KID} sitting across from each other in a diner booth, a paper placemat between them, "
                  "both holding fat markers and looking at the placemat, a ketchup bottle and a mug on the table. "
                  "Blue grown-up, yellow kid, pure white background. ", "1:1"),
    "story-4-3": ("Seen from above: a paper placemat on a diner table with one continuous loopy marker line on it, "
                  "a big hand with a blue marker coming in from the top edge and a small hand with a red marker coming "
                  "in from the bottom edge, both drawing the same line, motion ticks around both hands, a plate of "
                  "fries arriving at one corner. Pure white background. ", "1:1"),
    "story-4-4": (f"The same diner booth: {KID} on one side holding a red marker, and on the other side {ARM} holding "
                  "a green marker, both drawing on the paper placemat between them, radiating ticks over the kid's "
                  "head like an idea. Yellow kid, green robot arm, pure white background. ", "1:1"),
    # card 9, the crushed pen
    "story-9": (f"{ARM} pressing a fat red marker straight down into a small whiteboard on a table so hard that the "
                "marker's felt tip is squashed flat and splayed, the board bending under it, a big sweat drop on the "
                "arm, short straight motion lines around the tip. Green robot arm, red marker, pure white background. ",
                "16:9"),
    # card 10, the trigger that wasn't, then the button
    "story-10-1": (f"{ARM} with a small camera box on its wrist hovering over a completely blank whiteboard on a "
                   "table, big question marks around it, jittery short motion lines, a sweat drop. Green robot arm, "
                   "pure white background. ", "1:1"),
    "story-10-2": (f"{KID}'s hand pressing a big round green button on a table, and beside it {ARM} happily drawing "
                   "a loopy green line on a whiteboard, radiating ticks around the button. Yellow kid, green robot "
                   "arm, pure white background. ", "1:1"),
    # card 11, the error
    "story-11": (f"{KID} sitting at a laptop, leaning in and squinting at the screen; on the screen five plain "
                 "horizontal bars standing for lines of code, one bar sticking out to the left of the others and "
                 "circled in red, a red jagged burst popping out of the top of the screen, a sweat drop. Yellow kid, "
                 "pure white background. ", "16:9"),
    # card 12, the log
    "story-12": ("An open notebook lying on a table, its page divided into four empty boxes in a row, a hand holding "
                 "a fat marker filling the boxes with squiggle lines, a mug beside it, and in the background "
                 f"{ARM} holding a marker. Blue notebook lines, yellow hand, green robot arm, pure white background. ",
                 "16:9"),
    # card 14, the advice: one panel per line
    "story-14-1": (f"{KID} at a laptop whose screen shows a cartoon turtle drawing a square, and beside the laptop a "
                   "tiny simple outlined robot arm holding a marker drawing the very same square on a small "
                   "whiteboard, radiating ticks around both. Yellow kid, green turtle and robot arm, pure white "
                   "background. ", "16:9"),
    "story-14-2": ("Four small whiteboards standing in a row from left to right, each bigger than the last: the first "
                   "holds one small square, the second a square with a face, the third a creature made of loops, the "
                   f"fourth a crowded drawing of creatures and flowers; {KID} climbing them like stairs with a marker "
                   "in hand, radiating ticks. Red marker lines, yellow kid, pure white background. ", "16:9"),
}
JOBS = {name: (prompt + GRAMMAR, aspect) for name, (prompt, aspect) in STORIES.items()}


def generate(prompt: str, aspect: str, key: str) -> tuple[bytes, str]:
    """The pitch's call, at this deck's image size (the pitch hardcodes 2K)."""
    import base64, json, urllib.error, urllib.request
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect, "imageSize": SIZE}}}
    req = urllib.request.Request(pitch.URL, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}")
    cand = d.get("candidates", [{}])[0]
    for part in cand.get("content", {}).get("parts", []):
        if "inlineData" in part:
            return base64.b64decode(part["inlineData"]["data"]), part["inlineData"]["mimeType"]
    raise RuntimeError(f"no image, finishReason={cand.get('finishReason')}")


def main(argv: list[str]) -> None:
    force = "--force" in argv
    names = [a for a in argv if not a.startswith("--")] or list(JOBS)
    unknown = [n for n in names if n not in JOBS]
    if unknown:
        sys.exit(f"unknown job(s): {unknown}; choose from {list(JOBS)}")
    key = os.environ.get("GEMINI_API_KEY") or pitch.api_key()   # the env var first: a worktree has no .env
    IMG.mkdir(exist_ok=True)
    failed = []
    for name in names:
        prompt, aspect = JOBS[name]
        out = IMG / f"{name}.jpg"
        if out.exists() and not force:
            print(f"keep  {out.name}")
            continue
        try:
            data, mime = generate(prompt, aspect, key)
        except RuntimeError as e:
            print(f"FAIL  {name}: {e}")
            failed.append(name)
            continue
        tmp = IMG / f"{name}.{'png' if 'png' in mime else 'bin'}"
        tmp.write_bytes(data)
        pitch.to_jpeg(tmp, out)
        print(f"wrote {out.name} ({out.stat().st_size // 1024} KB)", flush=True)
    if failed:
        sys.exit(f"{len(failed)} job(s) failed: {failed}; rerun with those names to try again")


if __name__ == "__main__":
    main(sys.argv[1:])
