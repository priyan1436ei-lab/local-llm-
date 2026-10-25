# LocalCoder training datasets

This folder contains example prompt and evaluation data that can be used to test, benchmark, or fine-tune agent workflows around LocalCoder.

## Structure

- `prompts/feature_requests.jsonl` — new feature generation prompts
- `prompts/bug_fix_tasks.jsonl` — debugging and bug-fix tasks
- `evaluations/benchmark_tasks.jsonl` — benchmark-style tasks with expected keywords
- `examples/` — optional project snapshots, generated outputs, and validation traces

## Notes

Each JSONL row is a single training or evaluation example. Include the prompt, expected output, acceptance criteria, and optional metadata such as difficulty or domain.
