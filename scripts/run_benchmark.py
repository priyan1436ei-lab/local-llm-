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

    def evaluate(self, task: dict[str, Any], output: str) -> tuple[bool, float]:
        expected = task.get("expected_keywords") or []
        if isinstance(expected, str):
            expected = [expected]
        text = (output or "").lower()
        if not expected:
            return bool(text.strip()), 1.0 if text.strip() else 0.0
        matches = sum(1 for keyword in expected if keyword.lower() in text)
        score = matches / max(len(expected), 1)
        return matches == len(expected), score

    def run(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for task in self.load_tasks():
            output = task.get("output", "")
            passed, score = self.evaluate(task, output)
            results.append({
                "id": task.get("id", "unknown"),
                "prompt": task.get("prompt", ""),
                "passed": passed,
                "score": round(score, 3),
                "task_type": task.get("labels", {}).get("task_type") or task.get("task_type", "unknown"),
                "difficulty": task.get("labels", {}).get("difficulty") or task.get("difficulty", "unknown"),
                "domain": task.get("labels", {}).get("domain") or task.get("domain", "unknown"),
                "expected_keywords": task.get("expected_keywords", []),
                "output_preview": output[:300],
            })
        return results

    def summary(self, results: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        rows = results if results is not None else self.run()
        total = len(rows)
        passed = sum(1 for item in rows if item.get("passed"))
        avg_score = sum(float(item.get("score", 0.0)) for item in rows) / total if total else 0.0
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round((passed / total) * 100, 2) if total else 0.0,
            "average_score": round(avg_score, 3),
            "results": rows,
        }
