# LocalCoder RTX — Local AI Coding Agent for Priyan

GitHub repository: https://github.com/priyan1436ei-lab/local-llm-

A professional-grade local coding agent designed to run entirely on a developer's machine. It combines a local LLM, a workspace-aware tool loop, and a browser or CLI interface to allow natural-language software development without sending code to a cloud service.

This project is built for people who want:

- local-first AI coding
- transparent command execution
- real project editing inside a workspace
- safer experimentation with Ollama-hosted models
- a practical platform for training, evaluation, and AI workflow research

## Why this project matters

Most AI coding tools are either hosted in the cloud or restricted to a browser sandbox. LocalCoder takes a different approach: it brings the model, tool execution, and code editing loop onto the same machine.

This creates a workflow where the agent can:

- inspect a project folder
- read only necessary files
- make targeted code changes
- propose and run terminal commands
- debug failures using output from the terminal
- continue iterating until the task is complete

That makes it useful for rapid prototyping, app generation, debugging workflows, and local experimentation with open-source LLMs.

## Project highlights

- Local-first AI coding assistant
- Ollama integration for model-backed reasoning
- Browser UI and CLI support
- Workspace file read/write/edit tools
- Approval flow for shell command execution
- Automatic backups for overwritten files
- Safe path constraints inside the project workspace
- Lightweight architecture suitable for experimentation and research

## Architecture

The repository is organized around a simple but effective agent loop:

1. Load the user's prompt
2. Inspect the current workspace
3. Decide the next tool action
4. Read or edit the relevant files
5. Run tests, builds, or validation commands
6. Use the output to repair errors and continue
7. Finish when the task is complete or blocked

Core components:

- `localcoder/agent.py` — central coding agent loop and action schema
- `localcoder/tools.py` — workspace tools for listing, reading, writing, and command execution
- `localcoder/config.py` — model selection, VRAM-aware defaults, and runtime settings
- `localcoder/ollama_client.py` — interface to the Ollama server
- `localcoder/web.py` — browser-based UI backend
- `localcoder/ui.html` — frontend interface for the local browser app

## Agent behavior

The agent is designed to operate in a bounded iterative loop. It does not blindly generate code; it works through a tool-driven workflow.

Supported actions include:

- `list_files` for project exploration
- `read_file` for targeted inspection
- `write_file` to create or overwrite files
- `replace_in_file` for exact edits
- `run_command` to execute tests, builds, or scripts
- `finish` when the task is satisfied

Important safety features:

- workspace isolation: no access outside the working folder
- hidden metadata protection: `.git` and `.localcoder` are excluded
- command approval by default
- backups for overwritten files
- explicit trust required for destructive or unrestricted execution

## Professional LLM workflow

This project is not just a chatbot wrapper. It functions more like a local AI software agent:

- prompt-driven execution
- file-aware reasoning
- tool use grounded in project state
- iterative development based on test/build results
- step-limited autonomous behavior for practical control

This is especially useful for:

- building landing pages and web apps
- creating Python scripts and modules
- debugging failing code
- refining project structure iteratively
- collecting examples for fine-tuning or evaluation pipelines

## Dataset and training use cases

This repository is a strong foundation for local AI experimentation and dataset creation. While it is not a dedicated training framework by itself, it is highly useful for creating real-world AI development datasets.

A practical dataset structure could be:

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

Useful dataset fields:

- user prompt
- repository state before the task
- expected deliverable or acceptance criteria
- tool history and shell commands
- final code output
- validation/test results
- failure reason and repair attempts

This makes the project valuable for:

- supervised fine-tuning examples
- agent trajectory collection
- benchmark generation
- local LLM evaluation pipelines

## Example prompts

### Web app creation

```text
Build a responsive personal portfolio for Priyan using only HTML, CSS and JavaScript. Include hero, about, skills, projects and contact sections. Use a dark theme with lime accents. Write all files in the workspace.
```

### Existing project update

```text
Read the current project. Add a mobile menu and a theme switcher. Preserve the existing content.
```

### Python task with validation

```text
Create a Python calculator module with add, subtract, multiply and divide functions. Write unittest tests including division by zero. Run the tests and fix failures.
```

## Windows quick start

1. Install Python 3.10+ with the Windows launcher.
2. Install Ollama and keep it running.
3. Download the model from Ollama.
4. Run `START_HERE.bat` or launch the agent UI.
5. Open the local browser at `http://127.0.0.1:8765` if needed.
6. Enter a prompt and approve commands when prompted.

## Hardware recommendations

| GPU VRAM | Recommended model | Context |
|---|---|---|
| Unknown / 4 / 6 GB | qwen2.5-coder:3b | 4096 |
| 8 GB or more | qwen2.5-coder:7b | 4096 |

These are conservative defaults. Real performance depends on your GPU, CPU, RAM, and model size.

If memory is tight, consider:

```powershell
ollama pull qwen2.5-coder:1.5b
```

and reduce context size if needed.

## CLI usage

```powershell
py -3 -m localcoder --workspace workspace "Build a static todo website"
py -3 -m localcoder --workspace "C:\Projects\myrepo" --model qwen2.5-coder:3b --ctx 4096
py -3 -m unittest discover -s tests -v
```

Interactive mode:

- omit the prompt
- type `/exit` to quit
- shell commands require approval unless `--unsafe-commands` is used

## Security and trust model

This tool is intentionally local and explicit about trust boundaries.

Important notes:

- shell commands are not sandboxed
- generated programs can access your computer and network
- command approval is required by default
- file tools reject paths outside the workspace
- backups are stored under `.localcoder/backups`

Use this tool only in environments you trust.

## Validation and limitations

This project includes test coverage for orchestration, tool behavior, backups, approval flow, cancellation, and path protection. However, these tests validate system logic, not the quality of a specific LLM.

Current limitations:

- no full IDE editor
- no persistent cross-run memory by default
- no cloud deployment pipeline
- no advanced dataset ingestion system built in
- no full fine-tuning pipeline included

## Roadmap ideas

This project can be extended with:

- more robust project scaffolding templates
- better memory across sessions
- dataset collection and benchmark scripts
- stronger metric tracking for agent performance
- improved UI for task history and project summaries
- support for additional local model providers and routers

## License

This project is released under the MIT license. See `LICENSE` for details.

## Summary

LocalCoder RTX is a practical local AI coding agent built around the idea that real software work needs real file access, real tools, and real command execution. It is a strong base for local development, LLM experimentation, dataset collection, and AI-assisted engineering in a developer-controlled environment.

The project is especially valuable for anyone who wants a professional local AI coding workflow without depending on hosted APIs or remote infrastructure.
