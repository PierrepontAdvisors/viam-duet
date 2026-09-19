"""Inline tonight's real assets into the viewer mockup: photos as data URIs, plan SVG paths split into
human ink and robot strokes, the session history, and the calibration quad."""
import base64, json, re, sys, pathlib
sp = pathlib.Path(__file__).parent
assets = sp / "assets"
screen = pathlib.Path(".superpowers/brainstorm/89316-1789785696/content")
src, dst = sys.argv[1], sys.argv[2]

def data_uri(p): return "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode()
images = {"live": data_uri(assets / "live-small.jpg")}
for p in sorted(assets.glob("turn-*.jpg")):
    images[p.stem] = data_uri(p)

plans = {}
for p in sorted(assets.glob("plan-*.svg")):
    turn = int(p.stem.split("-")[1])
    ink, robot = [], []
    for m in re.finditer(r'<path d="([^"]+)"[^>]*stroke="([^"]+)"', p.read_text()):
        (robot if m.group(2) == "green" else ink).append(m.group(1))
    plans[turn] = {"ink": ink, "robot": robot}

history = json.loads(pathlib.Path("code/hackathon/sessions/20260918-190258/session.json").read_text())["history"]
calib = json.loads(pathlib.Path("code/hackathon/duet/data/calibration.json").read_text())
calib = {"marks_image": calib["marks_image"], "board_tl_index": calib["board_tl_index"],
         "board_mm": calib["board_mm"], "image_size": [1280, 720], "cam_to_robot": calib["cam_to_robot"]}

data = (f"const IMAGES = {json.dumps(images)};\nconst PLANS = {json.dumps(plans)};\n"
        f"const HISTORY = {json.dumps(history)};\nconst CALIB = {json.dumps(calib)};")
html = (sp / src).read_text().replace("/*__DATA__*/", data)
(screen / dst).write_text(html)
print(screen / dst, len(html), "plans:", {k: (len(v["ink"]), len(v["robot"])) for k, v in plans.items()})
