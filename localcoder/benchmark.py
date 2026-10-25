from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


class DatasetBuilder:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        return self.root / name

    def add_record(
        self,
        prompt: str,
        output: str,
        *,
        task_type: str = "feature_request",
        difficulty: str = "medium",
        domain: str = "general",
        status: str = "completed",
        expected_keywords: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        record = {
            "prompt": prompt,
            "output": output,
            "status": status,
            "labels": {
                "task_type": task_type,
                "difficulty": difficulty,
                "domain": domain,
            },
            "expected_keywords": expected_keywords or [],
            "metadata": metadata or {},
        }
        file_path = self._path("records.jsonl")
        with file_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return file_path

    def add_records(self, records: Iterable[dict[str, Any]]) -> list[Path]:
        created = []
        for item in records:
            created.append(
                self.add_record(
                    prompt=item["prompt"],
                    output=item.get("output", ""),
                    task_type=item.get("task_type", "feature_request"),
                    difficulty=item.get("difficulty", "medium"),
                    domain=item.get("domain", "general"),
                    status=item.get("status", "completed"),
                    expected_keywords=item.get("expected_keywords"),
                    metadata=item.get("metadata"),
                )
            )
        return created

    def load_records(self) -> list[dict[str, Any]]:
        file_path = self._path("records.jsonl")
        if not file_path.exists():
            return []
        records: list[dict[str, Any]] = []
        for line in file_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return records

    def filter_records(
        self,
        *,
        task_type: str | None = None,
        difficulty: str | None = None,
        domain: str | None = None,
    ) -> list[dict[str, Any]]:
        items = self.load_records()
        if task_type:
            items = [item for item in items if item.get("labels", {}).get("task_type") == task_type]
        if difficulty:
            items = [item for item in items if item.get("labels", {}).get("difficulty") == difficulty]
        if domain:
            items = [item for item in items if item.get("labels", {}).get("domain") == domain]
        return items

    def export_jsonl(
        self,
        file_path: str | Path,
        *,
        task_type: str | None = None,
        difficulty: str | None = None,
        domain: str | None = None,
    ) -> Path:
        target = Path(file_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        records = self.filter_records(task_type=task_type, difficulty=difficulty, domain=domain)
        with target.open("w", encoding="utf-8") as handle:
            for item in records:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        return target
