from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .agent import CodingAgent
from .config import Settings, detect_vram_gb
from .ollama_client import OllamaClient, OllamaError


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="localcoder",
        description="Local autonomous coding agent for Ollama + RTX 3050-class GPUs.",
    )
    parser.add_argument("prompt", nargs="*", help="Coding task. If omitted, interactive mode starts.")
    parser.add_argument("--workspace", default="workspace", help="Project folder the agent may edit.")
    parser.add_argument("--model", help="Override Ollama model, e.g. qwen2.5-coder:3b")
    parser.add_argument("--ctx", type=int, help="Override context tokens")
    parser.add_argument("--max-steps", type=int, help="Maximum autonomous actions")
    parser.add_argument(
        "--unsafe-commands",
        action="store_true",
        help="Auto-approve ALL commands. Only for trusted tasks; not sandboxed.",
    )
    args = parser.parse_args()

    settings = Settings.auto()
    if args.model:
        settings.model = args.model
    if args.ctx:
        settings.num_ctx = args.ctx
    if args.max_steps:
        settings.max_steps = args.max_steps

    vram = detect_vram_gb()
    vram_text = f"{vram:.1f} GB" if vram is not None else "not detected"
    print("LocalCoder")
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

    installed = {m.get("name", "") for m in tags.get("models", [])}
    base_names = {name.split(":")[0] for name in installed}
    if settings.model not in installed and settings.model.split(":")[0] not in base_names:
        print(f"WARNING: model may not be installed. Run: ollama pull {settings.model}\n")

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
