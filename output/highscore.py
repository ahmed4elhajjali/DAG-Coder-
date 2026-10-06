"""
Utility functions for persisting a single integer high‑score value to disk.

The module provides three public helpers:

* ``read_high_score(path)`` – Return the stored high score (int). If the file
  does not exist or is malformed, ``0`` is returned.

* ``write_high_score(path, score)`` – Write *score* to *path* safely. The
  write is performed atomically using a temporary file and ``os.replace`` so
  that a crash during the write never leaves a partially‑written file.

* ``update_high_score(path, new_score)`` – Compare *new_score* with the stored
  high score and, if it is greater, persist the new value using
  ``write_high_score``. The function returns the (possibly updated) high score.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


def _ensure_path(path: PathLike) -> Path:
    """Convert *path* to a ``Path`` object and ensure its parent directory exists."""
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def read_high_score(path: PathLike) -> int:
    """Read the high score from *path*; return 0 on any problem."""
    p = _ensure_path(path)

    if not p.is_file():
        return 0

    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return int(data)
    except (json.JSONDecodeError, ValueError, OSError):
        return 0


def write_high_score(path: PathLike, score: int) -> None:
    """Write *score* to *path* atomically."""
    if not isinstance(score, int):
        raise TypeError("score must be an integer")

    p = _ensure_path(path)
    data = json.dumps(score)

    fd, tmp_name = tempfile.mkstemp(dir=str(p.parent), prefix=".highscore_", text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
            tmp_file.write(data)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
        os.replace(tmp_name, str(p))
    finally:
        if Path(tmp_name).exists():
            try:
                Path(tmp_name).unlink()
            except OSError:
                pass


def update_high_score(path: PathLike, new_score: int) -> int:
    """Update the persisted high score if *new_score* is greater; return the result."""
    if not isinstance(new_score, int):
        raise TypeError("new_score must be an integer")

    current = read_high_score(path)
    if new_score > current:
        write_high_score(path, new_score)
        return new_score
    return current
