from orchestrator import plan
from workers import run_dag
from integrator import integrate, parse_files


def _emit(cb, event, **data):
    if cb:
        cb(event, **data)


async def run_pipeline(task: str, on_event=None, max_parallel: int | None = None):
    _emit(on_event, "planning")
    tasks = await plan(task)
    _emit(on_event, "plan", tasks=tasks)
    results = await run_dag(tasks, on_event, max_parallel)
    _emit(on_event, "integrating")
    final = await integrate(task, results)
    files = parse_files(final)
    _emit(on_event, "finished", files=files)
    return tasks, results, files
