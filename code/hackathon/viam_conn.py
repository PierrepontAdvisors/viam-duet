"""Connect to the hackathon machine with credentials from .env (never committed)."""
import os
from pathlib import Path

from viam.robot.client import RobotClient

ENV_PATH = Path(__file__).with_name(".env")


def load_env(path: Path = ENV_PATH) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


_env = {**load_env(), **os.environ}  # a real environment variable wins over .env

MACHINE_ADDRESS = _env.get("VIAM_MACHINE_ADDRESS", "")
API_KEY_ID = _env.get("VIAM_API_KEY_ID", "")
API_KEY = _env.get("VIAM_API_KEY", "")

ARM = _env.get("VIAM_ARM_NAME", "arm")
GRIPPER = _env.get("VIAM_GRIPPER_NAME", "gripper")
CAMERA = _env.get("VIAM_CAMERA_NAME", "cam")
MOTION = "builtin"


def require_credentials() -> None:
    missing = [
        name
        for name, value in (
            ("VIAM_MACHINE_ADDRESS", MACHINE_ADDRESS),
            ("VIAM_API_KEY_ID", API_KEY_ID),
            ("VIAM_API_KEY", API_KEY),
        )
        if not value
    ]
    if missing:
        raise SystemExit(
            f"missing {', '.join(missing)}. Copy .env.example to .env next to this file "
            "and paste the values from the machine's CONNECT tab."
        )


async def connect() -> RobotClient:
    require_credentials()
    opts = RobotClient.Options.with_api_key(api_key=API_KEY, api_key_id=API_KEY_ID)
    return await RobotClient.at_address(MACHINE_ADDRESS, opts)
