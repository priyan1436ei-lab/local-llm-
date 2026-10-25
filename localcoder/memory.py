from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .ollama_client import OllamaClient


class MemoryStore:
    def __init__(self, workspace: Path):
        self.workspace = workspace.resolve()
        self.root = self.workspace / ".localcoder"
        self.root.mkdir(parents=True, exist_ok=True)
        self.history_path = self.root / "history.jsonl"
        self.summary_path = self.root / "memory.json"

    def client(self, url: str) -> OllamaClient:
        return OllamaClient(url)

    def chat(self, **kwargs):
        client = OllamaClient(kwargs.pop("ollama_url", "http://127.0.0.1:11434"))
        return client.chat(**kwargs)

    def read_history(self) -> list[dict[str, Any]]:
        if not self.history_path.exists():
            return []
        entries: list[dict[str, Any]] = []
        for line in self.history_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return entries

    def record_task(self, prompt: str, result: str, status: str = "completed") -> None:
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": status,
            "prompt": prompt[:4000],
            "result": result[:4000],
        }
        history = self.read_history()
        history.append(entry)
        history = history[-50:]
        lines = [json.dumps(item, ensure_ascii=False) for item in history]
        self.history_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

        summary = {
            "updated_at": entry["timestamp"],
            "latest_status": status,
            "latest_prompt": entry["prompt"],
            "latest_result": entry["result"],
            "recent_count": len(history),
            "project_name": self.workspace.name,
        }
        self.summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    def project_context(self) -> str:
        history = self.read_history()
        if not history:
            return "No prior task memory for this project yet."
        recent = history[-5:]
        lines: list[str] = []
        for item in recent:
            lines.append(
                f"- {item.get('timestamp', 'unknown')} | {item.get('status', 'unknown')} | "
                f"{(item.get('prompt') or '')[:180]}"
            )
        return "\n".join(lines)
