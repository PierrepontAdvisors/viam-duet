"""build_assets.py (docs/duet/class) plans its conversions from a fixed table and skips existing outputs."""
import importlib.util
import pathlib

SCRIPT = pathlib.Path(__file__).resolve().parents[3] / "docs" / "duet" / "class" / "build_assets.py"
REPO = SCRIPT.parents[3]


def load():
    spec = importlib.util.spec_from_file_location("build_assets", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_jobs_skips_existing_outputs_unless_forced():
    m = load()
    every = [dst for _, dst in m.PHOTOS + m.CLIPS]
    assert m.jobs(set(every), force=False) == []
    assert [d for _, _, d in m.jobs(set(every), force=True)] == every
    assert [d for _, _, d in m.jobs(set(every) - {"video/team-2.mp4"}, force=False)] == ["video/team-2.mp4"]
    assert [k for k, _, _ in m.jobs(set(), force=False)] == ["photo"] * 4 + ["clip"] * 4


def test_table_is_the_spec_table():
    m = load()
    assert m.PHOTOS == [
        ("photo-setup.webp", "img/setup.jpg"),
        ("photo-door.webp", "img/door.jpg"),
        ("photo-crowd.webp", "img/crowd.jpg"),
        ("photo-medal.jpg", "img/medal.jpg"),
    ]
    assert [s for s, _ in m.CLIPS] == ["IMG_0016.MOV", "IMG_0018.mov", "IMG_0022.mov", "IMG_0024.mov"]
    assert [d for _, d in m.CLIPS] == [f"video/team-{n}.mp4" for n in (1, 2, 3, 4)]
    assert (m.MAX_SIDE, m.JPEG_QUALITY, m.CLIP_HEIGHT, m.CLIP_SECONDS) == (2000, 85, 720, 15)


def test_local_only_outputs_and_the_source_folder_are_gitignored():
    lines = (REPO / ".gitignore").read_text().splitlines()
    for rule in ["hackathon-videos/", "docs/duet/class/video/", "docs/duet/class/img/crowd.jpg", "docs/duet/class/img/medal.jpg"]:
        assert rule in lines, rule
