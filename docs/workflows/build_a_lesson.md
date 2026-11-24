# Workflow: Build a lesson

## Purpose

Use this procedure to build an evaluation lesson with traceable
requirements, executable examples, and evidence of verification.

The lesson plan records intended work and progress.
The lesson guide explains implemented behavior.
The notebook demonstrates that behavior.

## 1. Inspect

Read:
- Applicable AGENTS.md instructions.
- The relevant lesson plan.
- Previous lesson documentation and implementation.
- Setup instructions, tests, and notebook execution scripts.

Inspect:
- Current branch and working-tree changes.
- Available Python environment.
- Existing reusable functions and fixtures.
- Differences between recorded progress and actual code.

Output:
- A short summary of existing behavior.
- Missing prerequisites or inconsistencies.
- Relevant file paths.

Complete when the proposed work is grounded in the current repository.

## 2. Plan

Define:
- Learning objective.
- Inputs and expected outputs.
- Business rules and evidence limitations.
- Scope and exclusions.
- Files to add or modify.
- Acceptance criteria and verification methods.
- Small implementation slices.

Record assumptions and decisions in the lesson plan.

During an explicitly planning-only task, stop after producing the plan.
When implementation is already authorized, proceed within that scope.

Complete when each acceptance criterion has an observable verification
method and the next implementation slice is clear.

## 3. Implement a small slice

Build one coherent part of the lesson at a time.

Examples:
- Source fixtures and database loading.
- Reference calculations and focused tests.
- Notebook and companion explanation.

Keep reusable logic in modules rather than duplicating it in notebook cells.
Preserve earlier lessons and unrelated changes.

Complete when the slice works and is ready for verification.

## 4. Verify

Discover exact commands from the repository's setup documentation and
configuration. Do not invent successful command results.

As applicable:
- Run focused tests for changed behavior.
- Run existing regression checks.
- Execute notebooks with a fresh kernel.
- Confirm deterministic results and safe reruns.
- Check documentation links and example outputs.

Record:
- Command.
- Result.
- Relevant environment details.
- Failures or execution limitations.

A test pass demonstrates only what that test checks.
Notebook format validation is not notebook execution.

Complete when required checks pass, or limitations are explicitly
reported and the affected work remains marked unverified.

## 5. Review

Inspect the diff against the acceptance criteria.

Ask:
- Does the implementation match the business rules?
- Are expected results independently justified?
- Could the code and its verifier share the same mistake?
- Are missing data and genuine zero values distinguishable?
- Are claims limited to the available evidence?
- Does documentation accurately describe the code?
- Are any unrelated changes present?

Fix findings within the authorized scope and rerun affected checks.

Complete when findings are resolved or clearly recorded as outstanding.

## 6. Handoff

Update the lesson plan with:
- Completed slices.
- Verification evidence.
- Decisions and their rationale.
- Remaining limitations.
- The next concrete action.

Provide a concise summary:
- What changed.
- Why it changed.
- How it was verified.
- What the learner should inspect next.

Commit or push only when requested.

## Resuming in a new Codex session

Use this prompt, replacing the plan path as needed:

> Read AGENTS.md, docs/workflows/build_a_lesson.md, and
> docs/plans/01_reference_data.md.
> Verify recorded progress against the code and current Git state.
> Summarize the next incomplete slice and any blockers.
> If implementation is authorized in this request, implement that slice,
> run relevant checks, and update the plan with actual results.
> Preserve unrelated changes.

## Learner checkpoint

The learner should be able to explain:
1. What problem this lesson solves.
2. What each input artifact represents.
3. How the result is calculated.
4. What evidence supports the expected result.
5. What a passing result does not prove.

Record this checkpoint as complete only when the learner confirms it.
