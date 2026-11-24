# Working in this repository

## Purpose

This project teaches AI evaluation through a synthetic enterprise finance
agent. Lessons progressively introduce reference data, agent execution,
traces, deterministic checks, narrative review, and release evaluation.

Each lesson should help a technical reader explain:
- The problem being solved.
- The evidence available.
- The implementation.
- How correctness is checked.
- What remains unverified.

## Before starting work

1. Read this file and any applicable nested AGENTS.md instructions.
2. Read `docs/workflows/build_a_lesson.md`.
3. Read the relevant lesson plan under `docs/plans/`.
4. Inspect the current code and Git status.
5. Verify recorded progress against the actual implementation.

If documentation and code disagree, report the discrepancy. Do not assume
a planned feature already exists.

## Implementation conventions

- Follow existing repository structure and Python setup instructions.
- Put reusable logic in Python modules; use notebooks for explanation
  and executable demonstrations.
- Preserve existing lesson behavior unless the task explicitly changes it.
- Use deterministic synthetic fixtures and explicit dates where possible.
- Store monetary amounts as integer cents.
- Keep changes small enough for a learner to inspect.
- Preserve unrelated and uncommitted work.

## Evaluation integrity

- Separate candidate outputs, reference facts, and reviewer judgments.
- Do not use the agent's answer to establish its own expected result.
- Do not silently regenerate expected results just to make a test pass.
- Distinguish missing evidence, failed checks, and passed checks.
- Never describe authored reviews as live LLM judgments.
- Never claim SME approval unless an actual review is recorded.
- Keep evaluator-only reference artifacts out of future agent inputs.
- Explain the limits of each evaluation result.

## Data and credentials

- Use entirely synthetic business data and fictional examples.
- Do not include confidential client information.
- Do not read or print credentials when inspecting configuration.
- Never commit secrets or local environment files.

## Verification and completion

- Use the repository's documented test and notebook execution commands.
- Run checks appropriate to the change.
- Report what ran, what passed, what failed, and what could not run.
- Do not claim a notebook executed based only on file-format validation.
- Update the relevant lesson plan with results and remaining work.
- Keep planned, implemented, and verified status distinct.
- Do not mark human understanding or review complete on the user's behalf.

## Documentation boundaries

- `docs/plans/`: implementation requirements, decisions, and progress.
- `docs/lessons/`: explanations of implemented lessons for readers.
- `docs/workflows/`: contributor procedures.
- `notebooks/`: executable learning walkthroughs.

Keep personal Codex coaching separate from public lesson content.
Link to detailed guidance instead of duplicating it here.
