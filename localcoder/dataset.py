from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent import CodingAgent
from .benchmark import BenchmarkRunner
from .config import Settings, detect_vram_gb
from .dataset import DatasetBuilder
from .ollama_client import OllamaClient, OllamaError
from .router import ModelRouter


def generate_training_bundle(dataset_root: str | Path) -> int:
    root = Path(dataset_root)
    root.mkdir(parents=True, exist_ok=True)
    dataset = DatasetBuilder(root)

    records = [
        {
            "prompt": "Build a responsive portfolio landing page with a dark theme and lime accents.",
            "output": "The portfolio includes hero, about, skills, projects, and contact sections with a dark palette and lime accents.",
            "task_type": "feature_request",
            "difficulty": "easy",
            "domain": "web",
            "status": "completed",
            "expected_keywords": ["hero", "about", "skills", "projects", "contact", "dark", "lime"],
            "metadata": {"source": "starter-bundle"},
        },
        {
            "prompt": "Fix a Python calculator module that crashes on division by zero with a clear error message.",
            "output": "The calculator now checks for zero divisors and raises a clear ValueError message with unit tests.",
            "task_type": "bug_fix",
            "difficulty": "medium",
            "domain": "python",
            "status": "completed",
            "expected_keywords": ["zero", "divide", "ValueError", "test"],
            "metadata": {"source": "starter-bundle"},
        },
        {
            "prompt": "Create a task tracker with add, complete, and delete actions using plain JavaScript.",
            "output": "The app includes add, complete, and delete interactions with a clean task list interface.",
            "task_type": "feature_request",
            "difficulty": "medium",
            "domain": "javascript",
            "status": "completed",
            "expected_keywords": ["add", "complete", "delete", "task"],
            "metadata": {"source": "starter-bundle"},
        },
        {
            "prompt": "Fix the mobile menu in an HTML page that does not open on small screens.",
            "output": "The menu now opens correctly on narrow screens with responsive CSS and a toggle interaction.",
            "task_type": "bug_fix",
            "difficulty": "easy",
            "domain": "web",
            "status": "completed",
            "expected_keywords": ["mobile", "menu", "responsive", "toggle"],
            "metadata": {"source": "starter-bundle"},
        },
    ]

    for item in records:
        dataset.add_record(
            prompt=item["prompt"],
            output=item["output"],
            task_type=item["task_type"],
            difficulty=item["difficulty"],
            domain=item["domain"],
            status=item["status"],
            expected_keywords=item.get("expected_keywords"),
            metadata=item.get("metadata"),
        )

    print(f"Training bundle generated in {root}")
    return 0


def run_benchmark(tasks_path: str | Path, output_path: str | Path | None = None) -> int:
    runner = BenchmarkRunner(tasks_path)
    results = runner.run()
    summary = runner.summary(results)
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def export_training_dataset(dataset_root: str | Path, output_path: str | Path, *, task_type=None, difficulty=None, domain=None) -> int:
    builder = DatasetBuilder(dataset_root)
    export_path = builder.export_jsonl(
        output_path,
        task_type=task_type,
        difficulty=difficulty,
        domain=domain,
    )
    print(f"Training export created: {export_path}")
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
    parser.add_argument("--benchmark-output", help="Write benchmark JSON summary to a file.")
    parser.add_argument("--export-training", help="Export filtered training records to a JSONL file.")
    parser.add_argument("--dataset-root", default="data/training", help="Directory for generated dataset records.")
    parser.add_argument("--generate-training", action="store_true", help="Generate a starter training bundle in the dataset root.")
    parser.add_argument("--task-type", help="Filter exported records by task type.")
    parser.add_argument("--difficulty", help="Filter exported records by difficulty.")
    parser.add_argument("--domain", help="Filter exported records by domain.")
    parser.add_argument(
        "--unsafe-commands",
        action="store_true",
        help="Auto-approve ALL commands. Only for trusted tasks; not sandboxed.",
    )
    args = parser.parse_args()

    if args.generate_training:
        return generate_training_bundle(args.dataset_root)
    if args.benchmark:
        return run_benchmark(args.benchmark, args.benchmark_output)
    if args.export_training:
        return export_training_dataset(args.dataset_root, args.export_training, task_type=args.task_type, difficulty=args.difficulty, domain=args.domain)

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
