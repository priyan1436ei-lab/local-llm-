from __future__ import annotations

import os
import shutil
import time
import subprocess
from pathlib import Path


IGNORE_NAMES = {
    ".git", ".idea", ".vscode", "node_modules", ".next", "dist", "build",
    ".localcoder", "target", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache",
}

class ToolError(RuntimeError):
    pass


class WorkspaceTools:
    def __init__(self, root: Path, allow_any_command: bool = False):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.allow_any_command = allow_any_command
        self.approve = None

    def _path(self, relative: str) -> Path:
        p = (self.root / relative).resolve()
        try:
            p.relative_to(self.root)
        except ValueError as e:
            raise ToolError("Path escapes workspace; denied.") from e
        if any(part in {".git", ".localcoder"} for part in p.relative_to(self.root).parts):
            raise ToolError("Internal metadata path denied.")
        return p

    def list_files(self, max_files: int = 250) -> str:
        files: list[str] = []
        for base, dirs, names in os.walk(self.root):
            dirs[:] = [d for d in dirs if d not in IGNORE_NAMES]
            for name in names:
                p = Path(base) / name
                rel = p.relative_to(self.root).as_posix()
                files.append(rel)
                if len(files) >= max_files:
                    return "\n".join(files) + "\n...truncated..."
        return "\n".join(files) if files else "(workspace is empty)"

    def read_file(self, path: str, max_chars: int = 30000) -> str:
        p = self._path(path)
        if not p.exists() or not p.is_file():
            raise ToolError(f"File not found: {path}")
        data = p.read_text(encoding="utf-8", errors="replace")
        if len(data) > max_chars:
            return data[:max_chars] + "\n...truncated..."
        return data

    def write_file(self, path: str, content: str) -> str:
        p = self._path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        self.backup(p)
        p.write_text(content, encoding="utf-8")
        return f"Wrote {path} ({len(content)} chars)"

    def replace_in_file(self, path: str, find: str, replace: str) -> str:
        p = self._path(path)
        if not p.exists():
            raise ToolError(f"File not found: {path}")
        text = p.read_text(encoding="utf-8", errors="replace")
        count = text.count(find)
        if count == 0:
            raise ToolError("Exact find text not found.")
        if count > 1:
            raise ToolError(f"Find text occurs {count} times; make it more specific.")
        self.backup(p)
        p.write_text(text.replace(find, replace, 1), encoding="utf-8")
        return f"Replaced one block in {path}"

    def backup(self, path: Path):
        if path.is_file():
            dest = self.root / ".localcoder" / "backups" / str(time.time_ns()) / path.relative_to(self.root)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)

    def run_command(self, command: str, timeout: int = 120) -> str:
        cmd = command.strip()
        if not cmd:
            raise ToolError("Empty command")
        if not self.allow_any_command:
            approved = self.approve(cmd) if self.approve else input(
                f"Run shell command (can access your computer): {cmd}\nApprove? [y/N] "
            ).strip().lower() == "y"
            if not approved:
                raise ToolError("Command declined. Continue without executing it.")
        try:
            # Commands and generated programs are NOT sandboxed. Explicit trust is required.
            with __import__('tempfile').TemporaryFile() as output:
                proc = subprocess.Popen(cmd, cwd=self.root, shell=True, stdout=output,
                                        stderr=subprocess.STDOUT,
                                        start_new_session=(os.name != "nt"))
                try:
                    proc.wait(timeout=max(1, min(timeout, 600)))
                    status = f"exit_code={proc.returncode}"
                except subprocess.TimeoutExpired:
                    if os.name == "nt":
                        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                                       capture_output=True)
                    else:
                        import signal
                        os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
                    status = "Command timed out; process tree terminated"
                size = output.tell()
                output.seek(max(0, size - 16000))
                return status + "\n" + output.read().decode("utf-8", errors="replace")
        except OSError as exc:
            raise ToolError(str(exc)) from exc
