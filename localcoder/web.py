from __future__ import annotations

import argparse
from pathlib import Path

from .agent import CodingAgent
from .benchmark import BenchmarkRunner
from .config import Settings, detect_vram_gb
from .dataset import DatasetBuilder
from .ollama_client import OllamaClient, OllamaError
from .router import ModelRouter


def run_benchmark(tasks_path: str, output_path: str | None = None) -> int:
    runner = BenchmarkRunner(tasks_path)
    results = runner.run()
    summary = {
        "total": len(results),
        "passed": sum(1 for item in results if item["passed"]),
        "failed": sum(1 for item in results if not item["passed"]),
        "results": results,
    }
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(__import__("json").dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(__import__("json").dumps(summary, indent=2, ensure_ascii=False))
    return 0


def export_dataset(dataset_root: str, output_path: str) -> int:
    builder = DatasetBuilder(dataset_root)
    builder.add_record(
        "Create a small Python app with a health check endpoint.",
        "Flask app generated with /health route using a local acceptance check.",
        status="completed",
        metadata={"type": "example"},
    )
    builder.export_jsonl(output_path)
    print(f"Dataset exported to: {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="localcoder",
        description="Professional local-first coding agent for Ollama-powered LLM workflows.",
    )
    parser.add_argument("prompt", nargs="*", help="Coding task. If omitted, interactive mode starts.")
    parser.add_argument("--workspace", default="workspace", help="Project folder the agent may edit.")
    parser.add_argument("--model", help="Override Ollama model, e.g. qwen2.5-coder:3b")
    parser.add_argument("--ctx", type=int, help="Override context tokens")
    parser.add_argument("--max-steps", type=int, help="Maximum autonomous actions")
    parser.add_argument("--benchmark", help="Run a benchmark from a JSON/JSONL task file.")
    parser.add_argument("--export-dataset", help="Export dataset records to a JSONL file.")
    parser.add_argument("--dataset-root", default="data", help="Directory for generated dataset records.")
    parser.add_argument(
        "--unsafe-commands",
        action="store_true",
        help="Auto-approve ALL commands. Only for trusted tasks; not sandboxed.",
    )
    args = parser.parse_args()

    if args.benchmark:
        return run_benchmark(args.benchmark)
    if args.export_dataset:
        return export_dataset(args.dataset_root, args.export_dataset)

    settings = Settings.auto()
    if args.model:
        settings.model = args.model
    if args.ctx:
        settings.num_ctx = args.ctx
    if args.max_steps:
        settings.max_steps = args.max_steps

    vram = detect_vram_gb()
    vram_text = f"{vram:.1f} GB" if vram is not None else "not detected"
    print("LocalCoder RTX")
    print("Local-first LLM coding agent")
    print(f"GPU VRAM : {vram_text}")
    print(f"Model    : {settings.model}")
    print(f"Context  : {settings.num_ctx}")
    print(f"Workspace: {Path(args.workspace).resolve()}")
    print()

    client = OllamaClient(settings.ollama_url)
    try:
        tags = client.tags()
    except OllamaError as e:
        print(f"ERROR: {e}")
        print("Install/start Ollama, then pull the displayed model.")
        return 2

    available = {m.get("name", "") for m in tags.get("models", [])}
    router = ModelRouter(available)
    settings.model = router.choose(preferred=settings.model, vram_gb=vram)
    print(f"Selected model: {settings.model}")

    agent = CodingAgent(
        workspace=Path(args.workspace),
        settings=settings,
        allow_any_command=args.unsafe_commands,
    )

    initial = " ".join(args.prompt).strip()
    if initial:
        try:
            print("\n" + agent.run(initial))
            return 0
        except KeyboardInterrupt:
            print("\nStopped.")
            return 130
        except OllamaError as e:
            print(f"\nERROR: {e}")
            return 2

    print("Interactive mode. Type /exit to quit. Each prompt continues editing the same workspace.")
    while True:
        try:
            request = input("\nYou > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return 0
        if not request:
            continue
        if request.lower() in {"/exit", "exit", "quit"}:
            return 0
        try:
            result = agent.run(request)
            print(f"\nAgent > {result}")
        except OllamaError as e:
            print(f"ERROR: {e}")


if __name__ == "__main__":
    raise SystemExit(main())
