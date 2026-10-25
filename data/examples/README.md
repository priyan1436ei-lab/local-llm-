# LocalCoder RTX — dataset and training starter pack

This project now includes a lightweight training dataset starter set for prompt-driven local agent workflows.

## Included training data

- `data/prompts/feature_requests.jsonl` — examples for feature generation and landing page tasks
- `data/prompts/bug_fix_tasks.jsonl` — tasks for debugging and error repair loops
- `data/evaluations/benchmark_tasks.jsonl` — benchmark-style prompts with expected output keywords
- `data/README.md` — dataset structure and usage notes

## Example use

You can use these files to:

- test agent behavior on realistic prompts
- evaluate generated output against expected keywords
- create supervised examples for future fine-tuning
- collect task traces for local benchmarking

## Suggested workflow

1. Collect prompts from user requests or bug reports.
2. Capture the project state before task execution.
3. Log commands, file edits, and validation results.
4. Store successful and failed runs as training examples.
5. Export filtered results into a larger JSONL dataset for future model training.
