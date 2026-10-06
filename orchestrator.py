import json
from graphlib import TopologicalSorter
from llm import ask
from config import MAX_RETRIES

SYSTEM = """You are an orchestrator. Split the coding task into subtasks.
Return ONLY JSON: {"tasks":[{"id":"T1","title":"...","description":"...","depends_on":[]}]}
Make independent tasks have empty depends_on so they can run in parallel."""


def _clean(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        raw = raw.rsplit("```", 1)[0]
    return raw.strip()


async def plan(task: str) -> dict:
    last_err = None
    for _ in range(MAX_RETRIES):
        try:
            raw = await ask(SYSTEM, task, json_mode=True)
            tasks = {t["id"]: t for t in json.loads(_clean(raw))["tasks"]}
            for t in tasks.values():
                t.setdefault("depends_on", [])
            # validates the DAG (raises CycleError / KeyError on bad deps)
            TopologicalSorter({k: v["depends_on"] for k, v in tasks.items()}).prepare()
            for t in tasks.values():
                for d in t["depends_on"]:
                    if d not in tasks:
                        raise KeyError(f"unknown dependency {d}")
            return tasks
        except Exception as e:  # bad JSON / cycle -> retry
            last_err = e
    raise RuntimeError(f"Orchestrator failed after {MAX_RETRIES} tries: {last_err}")
