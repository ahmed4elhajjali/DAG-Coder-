import asyncio
import os

from groq import AsyncGroq

import config

_client = None
_loop = None


def set_api_key(key: str | None):
    """Override the key at runtime (used by the GUI)."""
    global _client
    if key:
        os.environ["GROQ_API_KEY"] = key
    _client = None


def _get():
    # one client per event loop (Streamlit calls asyncio.run on every run)
    global _client, _loop
    loop = asyncio.get_running_loop()
    if _client is None or _loop is not loop:
        _client, _loop = AsyncGroq(max_retries=5), loop  # auto-retry on 429
    return _client


async def ask(system: str, user: str, max_tokens: int = 4000, json_mode: bool = False) -> str:
    kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
    r = await _get().chat.completions.create(
        model=config.MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        **kwargs,
    )
    return r.choices[0].message.content
