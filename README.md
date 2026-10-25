# LocalCoder RTX — built for Priyan

A runnable local coding agent with browser UI and CLI. Give a prompt; it reads and writes actual project files, proposes shell commands, uses their results to repair errors, and continues for up to 28 actions. Uses an existing pretrained coding model through Ollama; this is not a newly trained LLM.

## Windows: start here

1. Extract this ZIP completely.
2. Install **Python 3.10+**, including the Windows `py` launcher: https://www.python.org/downloads/
3. Install **Ollama**, open it, and keep it running: https://ollama.com/download/windows
4. Double-click **START_HERE.bat**. It starts Ollama if needed, downloads the selected model if missing, then opens the agent UI.
5. Wait for the first model download. Open http://127.0.0.1:8765 if the browser does not open.
6. Leave the project folder blank to use `workspace`, or enter your project folder's full path.
7. Enter a prompt, click **Build project**, and approve commands when appropriate.

No pip packages or cloud API keys required. Initial Python/Ollama/model downloads require internet. Inference works offline after download. Dependency installation for generated projects may still require internet. Install Node.js separately for JavaScript projects, or relevant language runtimes as needed.

## First prompt

```text
Build a responsive personal portfolio for Priyan using only HTML, CSS and JavaScript. Include hero, about, skills, projects and contact sections. Use a dark theme with lime accents. Write all files into this workspace and include a README explaining how to open index.html. Do not install dependencies.
```

Then try:

```text
Read the current project. Add a mobile menu and a theme switcher. Preserve the existing content.
```

For Python:

```text
Create a Python calculator module with add, subtract, multiply and divide functions. Write unittest tests including division by zero. Run the tests and fix failures.
```

## Hardware profiles

| GPU VRAM | Automatic model | Context |
|---|---|---|
| Unknown / 4 / 6 GB | qwen2.5-coder:3b | 4096 |
| 8 GB or more | qwen2.5-coder:7b | 4096 |

These are conservative starting profiles, not GPU benchmark results or guaranteed VRAM fits. Ollama may offload layers to CPU depending on free VRAM and other processes. System RAM and context also matter. Check `ollama ps` during a task to see GPU/CPU allocation. Check `nvidia-smi` for GPU memory usage.

If memory is tight, use 2048 context or download the smaller model:

```powershell
ollama pull qwen2.5-coder:1.5b
```

Click **Refresh models** and select it. To try 7B manually, run `ollama pull qwen2.5-coder:7b`. The model catalog lists 3B at about 1.9 GB and 7B at about 4.7 GB; runtime memory is additional.

## What is included

- Local browser interface with installed model selection and progress polling.
- Workspace file listing, reading, writing and exact replacement.
- Model → tool → result → repair loop with bounded step count.
- Explicit approval for every shell command by default.
- Overwritten-file backups in `PROJECT/.localcoder/backups/TIMESTAMP/`.
- Session logs in `runs/` beside the launcher; these can contain your code/output.
- Cancellation between actions. An active model call can take up to 10 minutes to return; an active command ends on completion or its timeout. Stop does not undo edits.
- CLI mode and automated tests.

Backups are per overwritten file, not a complete transactional snapshot. To restore, stop the agent and copy the desired backed-up file to its original relative path. Newly created files have no previous version. Use Git for full project version control.

## Command execution and local access

File tools reject paths outside the project and internal `.git`/`.localcoder` metadata. Shell commands and generated programs **are not sandboxed** and can access your computer or network. The UI asks before each command; inspect it before approval. Use a disposable VM/container for untrusted code. Automatic file edits are limited to your selected project; select a dedicated folder, not your home directory.

The UI binds only to 127.0.0.1, checks the Host header and uses a per-launch request token. It is a single-user local tool; do not expose its port publicly. Generated HTML is shown as text, never executed in the agent UI.

## CLI

```powershell
py -3 -m localcoder --workspace workspace "Build a static todo website"
py -3 -m localcoder --workspace "C:\Projects\myrepo" --model qwen2.5-coder:3b --ctx 4096
py -3 -m unittest discover -s tests -v
```

Interactive CLI: omit the prompt; type `/exit` to quit. CLI requests command approval in the terminal. The `--unsafe-commands` flag auto-approves all shell execution and is only for explicitly trusted tasks. The browser intentionally has no auto-approval switch.

Linux/macOS: install Python/Ollama, pull the model, then run `python3 -m localcoder.web` from this folder. GPU support depends on your platform and Ollama.

## Troubleshooting

- **Ollama unavailable:** open Ollama or run `ollama serve`; retry Refresh models.
- **Model missing / HTTP 404:** `ollama pull qwen2.5-coder:3b`; choose the exact downloaded tag.
- **Slow or out of memory:** close GPU-heavy programs, use 1.5B/3B and 2048 context. Avoid large whole-repository prompts.
- **py not found:** install the Python Windows launcher, or run `python -m localcoder.web` manually.
- **Port 8765 already used:** stop the earlier LocalCoder process before restarting.
- **Step limit reached:** inspect the files and give a focused follow-up prompt.
- **Command fails:** approve a suitable fix proposed by the agent, or install the required runtime.

## Validation and limitations

Automated tests use a scripted fake model to validate orchestration, tool errors, backups, approval, cancellation and path protection. They do not measure real model quality. Real Ollama inference, Windows launcher execution and RTX 3050 performance were not tested in the build environment. Small local models can produce incomplete or incorrect code; work in small tasks and review/test outputs. A model's finish message alone is not proof of correctness.

This version has no fine-tuning pipeline, full IDE editor, deployment service or persistent model conversation between separate runs. Follow-up runs read current project files. Existing datasets are not automatically training the model.

Official references: https://ollama.com/library/qwen2.5-coder and https://docs.ollama.com/api/chat
"# local-llm-" 
