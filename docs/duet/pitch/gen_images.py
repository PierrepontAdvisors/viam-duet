"""Generate the deck's plate textures and hero illustrations with Nano Banana 2.

Reads GEMINI_API_KEY from code/hackathon/.env (gitignored), sends it in a header, writes JPEGs
into img/ beside this file. Skips images that already exist unless --force is given.

    python3 docs/duet/pitch/gen_images.py                # everything missing
    python3 docs/duet/pitch/gen_images.py plate-3        # one image
    python3 docs/duet/pitch/gen_images.py --force hero-duet
"""
import base64
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"
ENV = HERE.parents[2] / "code" / "hackathon" / ".env"
MODEL = "gemini-3.1-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
JPEG_QUALITY = "88"

GRAMMAR = (
    "Playful flat cartoon drawn with a thick uniform black marker outline and flat bright fills, no shading, "
    "no gradients, short straight motion lines radiating from anything that moves, simple rounded shapes. "
    "No text, no letters, no logos, no watermark."
)
PLATE = (
    "A doodle wallpaper: black marker doodles on a pure white background, scattered evenly across the whole "
    "image edge to edge like a notebook margin filled up, with no focal point and no empty areas: wavy lines, "
    "zigzags, little bursts of short straight lines, dots, small arcs{extra}. One uniform thick marker line "
    "with round ends, no shading. Black on white only, no colour, no people, no animals, no text."
)
PLATES = {
    "plate-1": PLATE.format(extra=", a few small spirals"),
    "plate-2": PLATE.format(extra=", a few tiny hearts drawn in one line"),
    "plate-3": PLATE.format(extra=", a few small stars drawn in one line"),
    "plate-4": PLATE.format(extra=", a few short dashed curves"),
    "plate-5": PLATE.format(extra=", a few small lightning bolts"),
    "plate-6": PLATE.format(extra=", a few small crosses"),
    "plate-7": (
        "A doodle wallpaper on a pure black background: marker doodles scattered evenly across the whole image "
        "edge to edge with no focal point and no empty areas: wavy lines, zigzags, little bursts of short straight "
        "lines, dots and small arcs, each doodle in one of five flat colours: yellow #ffd400, red #e5322d, blue "
        "#1f4fd6, green #17a34a, orange #ff7a00. One uniform thick marker line with round ends, no shading. "
        "No people, no animals, no text."
    ),
}
HEROES = {
    "hero-thesis": (
        "One simple outlined figure standing, holding an open book in one hand and a fat marker in the other, "
        "radiating ticks around the head as if lit up by an idea. Yellow figure on a pure white background. " + GRAMMAR
    ),
    "hero-duet": (
        "A simple outlined person and a simple outlined six-jointed robot arm drawing together on the same small "
        "whiteboard lying flat on a table, each holding a marker, motion ticks around both hands, one continuous "
        "loopy line on the board joining their two marks. Red person, green robot arm, pure white background. " + GRAMMAR
    ),
    "hero-build": (
        "A simple outlined figure dancing with both arms up beside a simple outlined robot arm holding a marker, "
        "radiating ticks around both, a few confetti dots. Yellow figure, green arm, pure white background. " + GRAMMAR
    ),
}
JOBS = {**{k: (v, "16:9") for k, v in PLATES.items()}, **{k: (v, "1:1") for k, v in HEROES.items()}}


def api_key() -> str:
    for line in ENV.read_text().splitlines():
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit(f"GEMINI_API_KEY not found in {ENV}")


def generate(prompt: str, aspect: str, key: str) -> tuple[bytes, str]:
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect, "imageSize": "2K"},
        },
    }
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
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


def to_jpeg(src: Path, dst: Path) -> None:
    subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", JPEG_QUALITY, str(src), "--out", str(dst)],
        check=True, capture_output=True,
    )
    src.unlink()


def main(argv: list[str]) -> None:
    force = "--force" in argv
    names = [a for a in argv if not a.startswith("--")] or list(JOBS)
    unknown = [n for n in names if n not in JOBS]
    if unknown:
        sys.exit(f"unknown job(s): {unknown}; choose from {list(JOBS)}")
    key = api_key()
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
        to_jpeg(tmp, out)
        print(f"wrote {out.name} ({out.stat().st_size // 1024} KB)", flush=True)
    if failed:
        sys.exit(f"{len(failed)} job(s) failed: {failed}; rerun with those names to try again")


if __name__ == "__main__":
    main(sys.argv[1:])
