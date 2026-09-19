"""Background-task helpers shared by the page server and the runner script. Its own module because
`run.py` imports `web.py`, and both start long-lived tasks that must not die in silence."""
from __future__ import annotations

import asyncio


def watch(task: asyncio.Task) -> asyncio.Task:
    """A background loop that dies silently is worse than one that dies loudly."""
    def died(t: asyncio.Task) -> None:
        if not t.cancelled() and t.exception() is not None:
            print(f"[task died] {t.get_name()}: {t.exception()!r}", flush=True)
    task.add_done_callback(died)
    return task
