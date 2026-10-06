import asyncio
import sys

from config import OUTPUT_DIR
from examples import EXAMPLES
from integrator import save_files
from pipeline import run_pipeline


def log(event, **d):
    if event == "plan":
        print("DAG:", {k: v["depends_on"] for k, v in d["tasks"].items()})
    elif event == "start":
        print(f"  -> start {d['tid']}")
    elif event == "done":
        print(f"  <- done  {d['tid']}")
    elif event == "integrating":
        print("Integrating...")


async def main(task: str):
    _, _, files = await run_pipeline(task, log)
    save_files(files, OUTPUT_DIR)
    for p in files:
        print("saved", f"{OUTPUT_DIR}/{p}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: python main.py "your coding task"   (or: python main.py --example)')
    task = list(EXAMPLES.values())[0] if sys.argv[1] == "--example" else " ".join(sys.argv[1:])
    asyncio.run(main(task))
