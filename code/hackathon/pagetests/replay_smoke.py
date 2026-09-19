"""Smoke check for the replay harness: snapshot order, a refused setting, the stream, the files."""
import asyncio
import json
import sys

import httpx
import websockets

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765"
WS = BASE.replace("http", "ws") + "/ws"


async def main() -> int:
    async with httpx.AsyncClient(base_url=BASE, timeout=5) as c:
        health = await c.get("/health")
        assert health.status_code == 200 and "state" in health.json(), health.text
        calib = (await c.get("/calibration.json")).json()
        assert calib["type"] == "calib" and len(calib["marks_image"]) == 4 and calib["image_size"] == [1280, 720]
        async with c.stream("GET", "/stream.mjpg?overlay=0") as r:
            first = await r.aiter_bytes().__anext__()
            assert first.startswith(b"--frame\r\nContent-Type: image/jpeg"), first[:40]
    async with websockets.connect(WS) as ws:
        first, second = json.loads(await ws.recv()), json.loads(await ws.recv())
        assert (first["type"], second["type"]) == ("calib", "state"), (first["type"], second["type"])
        assert second["session"] and second["artists"] == ["haring"] and "hand_guard" in second
        await ws.send(json.dumps({"type": "set", "length": "bogus"}))
        for _ in range(30):
            m = json.loads(await asyncio.wait_for(ws.recv(), 5))
            if m["type"] == "error":
                assert "length" in m["message"]
                break
        else:
            raise AssertionError("no error came back for a bad setting")
        await ws.send(json.dumps({"type": "set", "direction": "45", "energy": "0.7"}))
        for _ in range(30):
            m = json.loads(await asyncio.wait_for(ws.recv(), 5))
            if m["type"] == "state" and m["direction"] == 45 and m["energy"] == 0.7:
                break
        else:
            raise AssertionError("direction and energy were not echoed")
    print("replay harness ok")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
