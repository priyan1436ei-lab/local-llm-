from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass


def detect_vram_gb() -> float | None:
    """Return the largest NVIDIA GPU VRAM size in GiB, if nvidia-smi is available."""
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=memory.total",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        values = []
        for line in out.splitlines():
            m = re.search(r"([0-9.]+)", line)
            if m:
                values.append(float(m.group(1)) / 1024.0)
        return max(values) if values else None
    except Exception:
        return None


def choose_model(vram_gb: float | None) -> tuple[str, int]:
    override = os.getenv("LOCALCODER_MODEL")
    if override:
        ctx = int(os.getenv("LOCALCODER_CTX", "4096"))
        return override, ctx

    # Conservative defaults for RTX 3050-class cards.
    if vram_gb is None or vram_gb < 7.5:
        return "qwen2.5-coder:3b", 4096
    return "qwen2.5-coder:7b", 4096


@dataclass(slots=True)
class Settings:
    model: str
    num_ctx: int
    max_steps: int = 28
    temperature: float = 0.1
    ollama_url: str = "http://127.0.0.1:11434"

    @classmethod
    def auto(cls) -> "Settings":
        model, ctx = choose_model(detect_vram_gb())
        return cls(
            model=model,
            num_ctx=ctx,
            max_steps=int(os.getenv("LOCALCODER_MAX_STEPS", "28")),
            temperature=float(os.getenv("LOCALCODER_TEMPERATURE", "0.1")),
            ollama_url=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/"),
        )
