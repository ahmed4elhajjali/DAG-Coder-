import os
import re

from llm import ask

SYSTEM = """You are an integrator. Merge the sub-agent outputs into one consistent project.
Fix imports, naming conflicts, and duplicates. Output every file as `### path` followed by a code block."""

_FILE_RE = re.compile(r"###\s*`?(\S+?)`?\s*\n```\w*\n(.*?)```", re.S)


async def integrate(task: str, results: dict) -> str:
    parts = "\n\n".join(f"[{k}]\n{v}" for k, v in results.items())
    return await ask(SYSTEM, f"Original task: {task}\n\n{parts}", max_tokens=8000)


def parse_files(text: str) -> dict:
    files = {}
    for path, code in _FILE_RE.findall(text):
        norm = os.path.normpath(path)
        if os.path.isabs(norm) or norm.startswith(".."):
            continue  # never write outside the output dir
        files[norm.replace("\\", "/")] = code
    return files


def save_files(files: dict, out_dir: str):
    for path, code in files.items():
        full = os.path.join(out_dir, path)
        os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(code)
