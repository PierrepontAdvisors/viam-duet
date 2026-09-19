import pytest
from viam.proto.common import Pose

from duet import config as cfg
from duet.calib import BoardToRobot, dict_to_pose, load_poses, pose_to_dict, save_pose


def down(x, y, z):
    return Pose(x=x, y=y, z=z, o_x=0, o_y=0, o_z=-1, theta=0)


def flat_board():
    # top-left, top-right, bottom-left of a 279 x 216 board; board x runs along world y here
    return BoardToRobot.from_corners(down(300, -100, 5), down(300, 179, 5), down(84, -100, 5), 279, 216)


def test_corners_map_to_themselves():
    b = flat_board()
    tl, tr, bl = b.to_world(0, 0), b.to_world(279, 0), b.to_world(0, 216)
    assert (tl.x, tl.y, tl.z) == (300, -100, 5)
    assert (round(tr.x, 6), round(tr.y, 6)) == (300, 179)
    assert (round(bl.x, 6), round(bl.y, 6)) == (84, -100)


def test_center_lift_and_orientation():
    c = flat_board().to_world(139.5, 108, lift=20)
    assert (round(c.x, 6), round(c.y, 6), c.z) == (192, 39.5, 25)
    assert (c.o_x, c.o_y, c.o_z, c.theta) == (0, 0, -1, 0)


def test_tilted_plane_interpolates_z():
    b = BoardToRobot.from_corners(down(300, -100, 0), down(300, 179, 10), down(84, -100, 0), 279, 216)
    assert round(b.to_world(139.5, 0).z, 6) == 5


def test_pose_dict_roundtrip():
    p = down(1.5, 2.5, 3.5)
    assert dict_to_pose(pose_to_dict(p)) == p


def test_save_and_load_nested_names(tmp_path):
    path = tmp_path / "poses.json"
    save_pose("corner.tl", down(1, 2, 3), path)
    poses = save_pose("look", down(4, 5, 6), path)
    assert poses["corner"]["tl"]["z"] == 3
    assert load_poses(path)["look"]["x"] == 4


def test_from_poses_uses_corner_entries(tmp_path):
    path = tmp_path / "poses.json"
    save_pose("corner.tl", down(300, -100, 5), path)
    save_pose("corner.tr", down(300, 179, 5), path)
    save_pose("corner.bl", down(84, -100, 5), path)
    b = BoardToRobot.from_poses(load_poses(path))
    far = b.to_world(cfg.BOARD_W_MM, cfg.BOARD_H_MM)   # the far corner is tl + ex + ey whatever the size
    assert (round(far.x, 6), round(far.y, 6)) == (84, 179)


def test_far_corner_is_parallelogram_closure():
    far = flat_board().to_world(279, 216)
    assert (round(far.x, 6), round(far.y, 6), far.z) == (84, 179, 5)


def test_file_roundtrip_preserves_all_fields(tmp_path):
    path = tmp_path / "poses.json"
    original = Pose(x=1.5, y=-2.5, z=3.25, o_x=0.1, o_y=0.2, o_z=-0.97, theta=12.5)
    save_pose("corner.tl", original, path)
    assert dict_to_pose(load_poses(path)["corner"]["tl"]) == original


def test_from_poses_reports_missing_corners():
    with pytest.raises(ValueError, match="missing corner touch-offs: tr, bl"):
        BoardToRobot.from_poses({"corner": {"tl": pose_to_dict(down(0, 0, 0))}})


def test_fourth_corner_bends_the_surface_bilinearly(tmp_path):
    path = tmp_path / "poses.json"
    save_pose("corner.tl", down(300, -100, 5), path)
    save_pose("corner.tr", down(300, 179, 5), path)
    save_pose("corner.bl", down(84, -100, 5), path)
    save_pose("corner.br", down(84, 179, 4), path)          # the far corner sits 1 mm lower than the plane
    b = BoardToRobot.from_poses(load_poses(path))
    w, h = cfg.BOARD_W_MM, cfg.BOARD_H_MM
    assert round(b.to_world(0, 0).z, 6) == 5 and round(b.to_world(w, 0).z, 6) == 5 and round(b.to_world(0, h).z, 6) == 5
    assert round(b.to_world(w, h).z, 6) == 4                 # the measured corner is hit exactly
    assert round(b.to_world(w / 2, h / 2).z, 6) == 4.75      # and the middle bends a quarter of the way
    assert round(b.to_world(w / 2, 0).z, 6) == 5             # the untouched edges stay on the plane


def test_without_a_fourth_corner_nothing_changes(tmp_path):
    path = tmp_path / "poses.json"
    save_pose("corner.tl", down(300, -100, 5), path)
    save_pose("corner.tr", down(300, 179, 5), path)
    save_pose("corner.bl", down(84, -100, 5), path)
    b = BoardToRobot.from_poses(load_poses(path))
    assert b.warp == (0.0, 0.0, 0.0)
    assert round(b.to_world(cfg.BOARD_W_MM / 2, cfg.BOARD_H_MM / 2).z, 6) == 5
