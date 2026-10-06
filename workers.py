import asyncio
from graphlib import TopologicalSorter

import config
from llm import ask

SYSTEM = (
    "You are a coding sub-agent. Implement ONLY your subtask. "
    "Output code with filenames as `### path/to/file.py` headers, each followed by a code block."
)


def _emit(cb, event, **data):
    if cb:
        cb(event, **data)


async def run_dag(tasks: dict, on_event=None, max_parallel: int | None = None) -> dict:
    ts = TopologicalSorter({k: v["depends_on"] for k, v in tasks.items()})
    ts.prepare()
    results: dict = {}
    sem = asyncio.Semaphore(max_parallel or config.MAX_PARALLEL)

    async def work(tid):
        t = tasks[tid]
        ctx = "\n\n".join(f"[{d} output]\n{results[d]}" for d in t["depends_on"])
        async with sem:
            _emit(on_event, "start", tid=tid)
            try:
                out = await ask(
                    SYSTEM, f"Subtask: {t['title']}\n{t['description']}\n\nContext:\n{ctx}"
                )
            except Exception as e:
                _emit(on_event, "failed", tid=tid, error=str(e))
                raise
            _emit(on_event, "done", tid=tid, output=out)
        return tid, out

    running: set = set()
    while ts.is_active():
        for tid in ts.get_ready():
            running.add(asyncio.create_task(work(tid)))
        done, running = await asyncio.wait(running, return_when=asyncio.FIRST_COMPLETED)
        for d in done:
            tid, out = d.result()
            results[tid] = out
            ts.done(tid)
    return results
