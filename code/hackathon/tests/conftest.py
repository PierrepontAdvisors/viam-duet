"""Shared fixtures: the day-1 calibration and real photos from the straight-down look pose."""
import json

import cv2
import numpy as np
import pytest

from duet import config as cfg


def _read(name: str) -> np.ndarray:
    img = cv2.imread(str(cfg.FIXTURES_DIR / name))
    assert img is not None, f"fixture {name} missing"
    return img


@pytest.fixture(scope="session")
def calibration() -> dict:
    return json.loads(cfg.CALIBRATION_PATH.read_text())


@pytest.fixture(scope="session")
def look_frame() -> np.ndarray:
    """A raw 1280 x 720 frame from the look pose (captures/calib_frame.jpg, 2026-09-18 18:58)."""
    return _read("look_frame.jpg")


@pytest.fixture(scope="session")
def exchange_start() -> np.ndarray:
    """Warped board before the first hardware exchange (sessions/20260918-185927)."""
    return _read("exchange-00-start.jpg")


@pytest.fixture(scope="session")
def exchange_human() -> np.ndarray:
    """The same board after the visitor drew: 13 strokes."""
    return _read("exchange-01-human.jpg")


@pytest.fixture(scope="session")
def exchange_robot() -> np.ndarray:
    """The same board after the robot answered."""
    return _read("exchange-01-robot.jpg")


@pytest.fixture(scope="session")
def board_blank() -> np.ndarray:
    """A warped board with no visitor ink."""
    return _read("board_blank.jpg")
