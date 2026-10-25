from __future__ import annotations

from typing import Iterable


DEFAULT_MODEL_PRIORITY = [
    "qwen2.5-coder:7b",
    "qwen2.5-coder:3b",
    "qwen2.5-coder:1.5b",
]


class ModelRouter:
    def __init__(self, available_models: Iterable[str] | None = None):
        self.available_models = list(available_models or [])

    def choose(self, preferred: str | None = None, vram_gb: float | None = None) -> str:
        if preferred and preferred in self.available_models:
            return preferred

        candidates = list(self.available_models)
        if preferred and preferred not in candidates:
            candidates.insert(0, preferred)

        if vram_gb is not None:
            if vram_gb < 4:
                low = [m for m in candidates if "1.5b" in m.lower()]
                if low:
                    return low[0]
            if vram_gb < 8:
                mid = [m for m in candidates if "3b" in m.lower()]
                if mid:
                    return mid[0]

        for name in DEFAULT_MODEL_PRIORITY:
            if name in candidates:
                return name
        return candidates[0] if candidates else (preferred or DEFAULT_MODEL_PRIORITY[0])

    def fallback_sequence(self, preferred: str | None = None, vram_gb: float | None = None) -> list[str]:
        chosen = self.choose(preferred=preferred, vram_gb=vram_gb)
        seq = [chosen]
        for candidate in self.available_models + [m for m in DEFAULT_MODEL_PRIORITY if m not in self.available_models]:
            if candidate not in seq:
                seq.append(candidate)
        return seq[:5]
