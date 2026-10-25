from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class BenchmarkRunner:
    def __init__(self, tasks_path: str | Path):
        self.tasks_path = Path(tasks_path)

    def load_tasks(self) -> list[dict[str, Any]]:
        if not self.tasks_path.exists():
            raise FileNotFoundError(f"Benchmark tasks file not found: {self.tasks_path}")
        tasks: list[dict[str, Any]] = []
        for raw_line in self.tasks_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not raw_line.strip():
                continue
            try:
                item = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            tasks.append(item)
        return tasks

    def evaluate(self, task: dict[str, Any], output: str) -> bool:
        expected = task.get("expected_keywords") or []
        if isinstance(expected, str):
            expected = [expected]
        if not expected:
            return bool(output.strip())
        lower = output.lower()
        return all(keyword.lower() in lower for keyword in expected)

    def run(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for task in self.load_tasks():
            prompt = task.get("prompt", "")
            output = task.get("output", "")
            passed = self.evaluate(task, output)
            results.append({
                "id": task.get("id", "unknown"),
                "prompt": prompt,
                "passed": passed,
                "expected_keywords": task.get("expected_keywords", []),
                "output_preview": output[:300],
            })
        return results
