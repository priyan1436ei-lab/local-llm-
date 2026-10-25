from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DatasetBuilder:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def add_record(
        self,
        prompt: str,
        output: str,
        status: str = "completed",
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        data = {
            "prompt": prompt,
            "output": output,
            "status": status,
            "metadata": metadata or {},
        }
        file_path = self.root / "records.jsonl"
        with file_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(data, ensure_ascii=False) + "\n")
        return file_path

    def export_jsonl(self, file_path: str | Path) -> Path:
        target = Path(file_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        records: list[dict[str, Any]] = []
        if (self.root / "records.jsonl").exists():
            for line in (self.root / "records.jsonl").read_text(encoding="utf-8", errors="replace").splitlines():
                if not line.strip():
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        with target.open("w", encoding="utf-8") as handle:
            for item in records:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        return target
