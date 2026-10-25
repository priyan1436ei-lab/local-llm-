# LocalCoder RTX — built for Priyan

A runnable local coding agent with browser UI and CLI. Give a prompt; it reads and writes actual project files, proposes shell commands, uses their results to repair errors, and continues for up to a bounded number of steps until the task is done or it is blocked.

This project is designed to run on your own machine. It keeps the model, tools, and project files local, so you can work without relying on a hosted API or cloud IDE.

## Project overview

LocalCoder combines three parts:

- A local Ollama model for reasoning and code generation
- A workspace-aware tool loop for reading, editing, and running commands
- A browser UI or CLI for prompting and approval

The core agent logic lives in `localcoder/agent.py` and the workspace tool layer is in `localcoder/tools.py`. The UI is served by `localcoder/web.py`, and the Ollama integration is handled in `localcoder/ollama_client.py`.

## Why this project exists

Many coding agents assume cloud access, browser-based editors, or remote infrastructure. This one is built for a local developer workflow:

- Open a project folder
- Ask for a feature, bug fix, or site build
- Let the agent inspect files and plan changes
- Approve shell commands before execution
- Iterate until the project runs

This makes it useful for:

- quick prototypes
- local app generation
- experimenting with open-source coding models
- learning how agentic workflows behave on real codebases

## Agent architecture

The agent follows a simple repeat-until-done pattern:

1. Inspect the current workspace
2. Read only the files needed for the task
3. Decide the next tool action
4. Execute one action at a time
5. Review command output or file errors
6. Fix the issue and continue
7. Finish when the task is complete

Supported actions in the core loop include:

- `list_files` to inspect the project tree
- `read_file` to open specific source files
- `write_file` to create or overwrite a file
- `replace_in_file` to perform an exact edit
- `run_command` to execute build, test, or dev commands
- `finish` to stop once the request is satisfied

The agent is intentionally conservative:

- it never leaves the workspace
- it avoids destructive commands by default
- it requires command approval unless `--unsafe-commands` is explicitly enabled
- it keeps backups of overwritten files in `.localcoder/backups/`
- it records session activity near the launcher for later review

## Dataset and training notes

This repository is not a full fine-tuning or dataset-training pipeline in the traditional ML sense. It is primarily an agent runner and local tool system for coding tasks. However, it is useful as a base for building a dataset-driven workflow.

### What the project does today

- Uses a local Ollama model for code generation and reasoning
- Creates an instruction-following workflow around a workspace
- Executes real commands against a project, not just static templates
- Captures outputs, logs, and generated files from each session

### How you can structure your own dataset

If you want to build a dataset around this project, a practical setup could look like this:

```text
data/
  prompts/
    feature_requests.jsonl
    bug_fix_tasks.jsonl
  examples/
    working_projects/
    failing_projects/
  evaluations/
    benchmark_prompts.txt
  outputs/
    generated_code/
    test_results/
```

A good dataset entry can include:

- task description or user prompt
- initial project state
- expected output or acceptance criteria
- command history
- final file content or result summary

For custom training flows, you can collect:

- successful prompt-to-project examples
- failed runs and their debug traces
- repaired code after test failures
- generated tests and corresponding fixes

This is especially useful for creating supervised examples for future fine-tuning or evaluation pipelines.

### Training mindset for this project

The repo is best understood as a local “agent training sandbox” instead of a standalone model trainer. In other words, you can use it to:

- test prompt quality
- measure how well a model handles repo editing tasks
- collect examples of agent behavior
- benchmark success/failure loops on real projects

If you later want to train a model, the patterns in this project are a good source for:

- instruction-response pairs
- code generation tasks
- bug fixing trajectories
- tool-use sequences

## Example workflows

### Build a website

```text
Build a responsive personal portfolio for Priyan using only HTML, CSS and JavaScript. Include hero, about, skills, projects and contact sections. Use a dark theme with lime accents. Write all files in the workspace.
```

### Improve an existing project

```text
Read the current project. Add a mobile menu and a theme switcher. Preserve the existing content.
```

### Build Python logic and validate it

```text
Create a Python calculator module with add, subtract, multiply and divide functions. Write unittest tests including division by zero. Run the tests and fix failures.
```

## Windows: start here

1. Extract this ZIP completely.
2. Install **Python 3.10+**, including the Windows `py` launcher: https://www.python.org/downloads/
3. Install **Ollama**, open it, and keep it running: https://ollama.com/download/windows
4. Double-click **START_HERE.bat**. It starts Ollama if needed, downloads the selected model if missing, then opens the agent UI.
5. Wait for the first model download. Open http://127.0.0.1:8765 if the browser does not open.
6. Leave the project folder blank to use `workspace`, or enter your project folder's full path.
7. Enter a prompt, click **Build project**, and approve commands when appropriate.

No pip packages or cloud API keys required. Initial Python/Ollama/model downloads require internet. Inference works offline after download. Dependency installation for generated projects may still require network access if the generated app installs packages.

## First prompt

```text
Build a responsive personal portfolio for Priyan using only HTML, CSS and JavaScript. Include hero, about, skills, projects and contact sections. Use a dark theme with lime accents. Write all files in the workspace.
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

These are conservative starting profiles, not GPU benchmark results or guaranteed VRAM fits. Ollama may offload layers to CPU depending on free VRAM and other processes. System RAM and context also matter.

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

Backups are per overwritten file, not a complete transactional snapshot. To restore, stop the agent and copy the desired backed-up file to its original relative path. Newly created files have no backup until they are overwritten.

## Command execution and local access

File tools reject paths outside the project and internal `.git`/`.localcoder` metadata. Shell commands and generated programs **are not sandboxed** and can access your computer or network. The UI itself is local-only and intended to be run by a single user.

The UI binds only to 127.0.0.1, checks the Host header and uses a per-launch request token. It is a single-user local tool; do not expose its port publicly. Generated HTML is shown as text, never as raw page output, and the interface is meant to stay local to the machine it is running on.

## CLI

```powershell
py -3 -m localcoder --workspace workspace "Build a static todo website"
py -3 -m localcoder --workspace "C:\Projects\myrepo" --model qwen2.5-coder:3b --ctx 4096
py -3 -m unittest discover -s tests -v
```

Interactive CLI: omit the prompt; type `/exit` to quit. CLI requests command approval in the terminal. The `--unsafe-commands` flag auto-approves all shell execution and is only for explicitly trusted workflows.

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

Automated tests use a scripted fake model to validate orchestration, tool errors, backups, approval, cancellation and path protection. They do not measure real model quality. Real Ollama inference still depends on the model and your hardware.

This version has no fine-tuning pipeline, full IDE editor, deployment service or persistent model conversation between separate runs. Follow-up runs read current project files. Existing datasets are not automatically imported into the tool loop; they must be prepared by the user if you want to build a training or evaluation dataset around the agent.

Official references: https://ollama.com/library/qwen2.5-coder and https://docs.ollama.com/api/chat

# local-llm-

This repository is a compact local-first coding agent environment built around Ollama and a filesystem-aware tool loop. It is designed for prompt-driven app generation, editing, and iterative debugging without sending code to a remote service.

If you want to extend it, the most productive next steps are:

- add richer project scaffolding templates
- build dataset collection scripts for prompt-to-output examples
- add stronger model evaluation and benchmarking
- improve agent memory and project context handling
- expand browser UX for task history and project summaries

The system is intentionally simple and transparent: a local model, a file tool layer, a command approval gate, and a loop that tries again after errors.
