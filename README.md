# Finance Agent Evaluation Lab

Executable lessons for evaluating a fictional enterprise finance assistant. All records and policy examples are synthetic.

## Start here

Follow [VS Code setup for Ubuntu WSL or Windows PowerShell](docs/setup.md), then open [Notebook 00](notebooks/00_success_contract.ipynb).

Lesson 00 demonstrates that a numerically correct answer can fail when its explanation is unsupported. It checks scope, periods, amounts, and a supplied narrative-review verdict. Reviews are explicitly demo-authored; this is not an automated semantic judge or a live agent benchmark.

## Implemented

- Project-local virtual environment instructions and Jupyter kernel selection.
- Offline success-contract notebook with three authored candidate answers.
- Structured per-check verdicts including `unverifiable` when review evidence is missing or stale.
- Seven regression tests and a fresh-kernel notebook runner.

## Next

01: synthetic database and independent goldens; 02: Azure OpenAI agent and traces; 03: deeper deterministic graders; 04: genuine MCP and trajectory checks; 05: multi-turn evaluation; 06: actual state/isolation; 07: calibrated LLM judge; 08: comparisons; 09: efficiency; 10: CI release reports; 11: feedback/drift.

The current notebook uses authored answers and known reference totals. It does not implement database access, MCP, live model calls, a general prose evaluator, or production release gates yet. Missing reviews never count as successful tasks. Finance approval is pending; no SME approval is claimed.

Shared logic is in `src/finance_evals`; evaluator-only examples and references are under `evals/`. Future agent access must exclude evaluator-only data. Private learning notes and client material do not belong in this public repository.
