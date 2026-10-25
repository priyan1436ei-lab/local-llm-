#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from localcoder.dataset import DatasetBuilder


def main() -> int:
    parser = argparse.ArgumentParser(description="Export filtered LocalCoder training records to JSONL.")
    parser.add_argument("dataset_root", help="Root directory containing records.jsonl")
    parser.add_argument("output_path", help="Where to write the exported JSONL dataset")
    parser.add_argument("--task-type", help="Filter: feature_request, bug_fix, benchmark, etc.")
    parser.add_argument("--difficulty", help="Filter: easy, medium, hard")
    parser.add_argument("--domain", help="Filter by domain name")
    args = parser.parse_args()

    builder = DatasetBuilder(args.dataset_root)
    builder.export_jsonl(
        args.output_path,
        task_type=args.task_type,
        difficulty=args.difficulty,
        domain=args.domain,
    )
    print(f"Exported dataset: {Path(args.output_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
