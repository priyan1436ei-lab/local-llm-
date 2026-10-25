from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import Settings
from .memory import MemoryStore
from .ollama_client import OllamaError
from .tools import ToolError, WorkspaceTools


ACTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "thought_summary": {"type": "string"},
        "action": {
            "type": "string",
            "enum": [
                "list_files", "read_file", "write_file", "replace_in_file",
                "run_command", "finish"
            ],
        },
        "path": {"type": "string"},
        "content": {"type": "string"},
        "find": {"type": "string"},
        "replace": {"type": "string"},
        "command": {"type": "string"},
        "timeout": {"type": "integer", "minimum": 1, "maximum": 600},
        "message": {"type": "string"},
    },
    "required": ["thought_summary", "action"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = r"""You are LocalCoder, an autonomous coding agent running on the user's computer.
Your job is to turn the user's coding request into working code inside ONE workspace.

You operate one action at a time. Available actions:
- list_files: inspect repository tree.
- read_file: read one text file. Requires path.
- write_file: create/overwrite a text file. Requires path + content.
- replace_in_file: exact single replacement. Requires path + find + replace.
- run_command: run a development command. Requires command. Prefer tests/build/lint over destructive commands.
- finish: only after the request is implemented or you are truly blocked. Put concise result in message.

Rules:
1. Never access paths outside the workspace.
2. Inspect existing files before changing an existing project.
3. For a new project, create the minimum complete runnable structure, not snippets.
4. Preserve user code unless changes are necessary.
5. Never claim a test passed unless you actually ran it and saw exit_code=0.
6. When a command/test fails, read the error, fix it, and retry.
7. Avoid huge files in one step when smaller modules are clearer.
8. Do not expose secrets or request API keys unless the user's requested integration fundamentally needs them.
9. Do not run destructive system/admin commands.
10. Keep thought_summary short; it is a progress note, not private chain-of-thought.
11. Output ONLY the JSON object matching the required schema.
"""


class CodingAgent:
    def __init__(
        self,
        workspace: Path,
        settings: Settings,
        allow_any_command: bool = False,
        verbose: bool = True,
    ):
        self.settings = settings
        self.memory = MemoryStore(workspace)
        self.client = self.memory.client(settings.ollama_url)
        self.tools = WorkspaceTools(workspace, allow_any_command=allow_any_command)
        self.verbose = verbose
        self.on_event = lambda event: None
        self.cancelled = lambda: False

    def _tool_result(self, action: dict[str, Any]) -> str:
        kind = action["action"]
        if kind == "list_files":
            return self.tools.list_files()
        if kind == "read_file":
            return self.tools.read_file(action.get("path", ""))
        if kind == "write_file":
            return self.tools.write_file(action.get("path", ""), action.get("content", ""))
        if kind == "replace_in_file":
            return self.tools.replace_in_file(
                action.get("path", ""), action.get("find", ""), action.get("replace", "")
            )
        if kind == "run_command":
            return self.tools.run_command(
                action.get("command", ""), int(action.get("timeout") or 120)
            )
        raise ToolError(f"Unknown action: {kind}")

    def run(self, request: str) -> str:
        files = self.tools.list_files(max_files=120)
        recent_context = self.memory.project_context()
        messages: list[dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"USER REQUEST:\n{request}\n\n"
                    f"INITIAL WORKSPACE FILES:\n{files}\n\n"
                    f"RECENT PROJECT MEMORY:\n{recent_context}\n\n"
                    "Start working."
                ),
            },
        ]

        for step in range(1, self.settings.max_steps + 1):
            if self.cancelled():
                message = "Stopped by user. Files already written are retained."
                self.memory.record_task(request, message, status="stopped")
                return message
            budget = max(2000, (self.settings.num_ctx - 1800) * 2)
            while len(messages) > 4 and sum(len(m["content"]) for m in messages) > budget:
                del messages[2:4]
            action = self.memory.chat(
                model=self.settings.model,
                messages=messages,
                schema=ACTION_SCHEMA,
                num_ctx=self.settings.num_ctx,
                temperature=self.settings.temperature,
            )
            if not isinstance(action, dict):
                raise OllamaError("Model action must be a JSON object; retry with a smaller task.")
            if self.cancelled():
                message = "Stopped by user. Files already written are retained."
                self.memory.record_task(request, message, status="stopped")
                return message
            summary = action.get("thought_summary", "")
            kind = action.get("action")
            self.on_event({"step": step, "action": kind, "summary": summary})
            if self.verbose:
                print(f"[{step:02d}] {kind}: {summary}")

            if kind == "finish":
                finished_message = action.get("message") or "Done."
                self.memory.record_task(request, finished_message, status="completed")
                return finished_message

            try:
                result = self._tool_result(action)
            except (ToolError, OSError) as e:
                result = f"TOOL_ERROR: {e}"

            result = result[:7000]
            self.on_event({"step": step, "result": result})
            if self.verbose:
                preview = result if len(result) < 800 else result[:800] + "..."
                print(preview)

            messages.append({"role": "assistant", "content": json.dumps(action, ensure_ascii=False)})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"RESULT OF ACTION {kind}:\n{result}\n\n"
                        "Continue with the next best single action."
                    ),
                }
            )

            if len(messages) > 18:
                messages = [messages[0], messages[1]] + messages[-14:]

        final_message = f"Stopped after {self.settings.max_steps} steps. Review current workspace and continue with another prompt."
        self.memory.record_task(request, final_message, status="stopped")
        return final_message
