#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from localcoder.benchmark import BenchmarkRunner


def main() -> int:
    parser = argparse.ArgumentParser(description="Run LocalCoder benchmark tasks and print summary.")
    parser.add_argument("tasks_path", help="Path to a JSON/JSONL file with benchmark tasks.")
    parser.add_argument("--output", help="Optional file to write the summary JSON to.")
    args = parser.parse_args()

    runner = BenchmarkRunner(args.tasks_path)
    results = runner.run()
    summary = runner.summary(results)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
