# Lesson 01: Building trustworthy reference data

Status: Draft plan — implementation not started.

## Learning objective

Understand how synthetic source records become reproducible expected
results for a finance-agent evaluation.

By the end of the lesson, the learner should be able to distinguish:
- Source business records.
- A reference calculation.
- A versioned evaluation case.
- A candidate answer.
- A reviewer judgment.

## Connection to Lesson 00

Lesson 00 evaluates authored candidate answers against supplied reference
facts and supplied narrative reviews.

Lesson 01 explains where the reference facts can come from and how to
verify them independently.

The [Lesson 00 guide](../lessons/00_success_contract.md) and
[notebook](../../notebooks/00_success_contract.ipynb) demonstrate the
[evaluator](../../src/finance_evals/contracts.py) using
[authored answers](../../evals/cases/lesson00_answers.json),
[supplied reference facts](../../evals/reference/revenue_case.json), and
[authored narrative reviews](../../evals/reviews/lesson00_reviews.json).
The [regression tests](../../tests/test_contracts.py) exercise the same inputs.

The evaluator compares the supplied numerical fields by value and type.
The reference currently stores the percentage as the string `"-10.00"`
and the monetary amounts as integer cents.

## Business question

> Why did Marketplace revenue decline last month?

For this synthetic case, fix the reporting date at 2026-11-18.

Compare:
- Prior period: September 2026.
- Current reporting period: October 2026.

November is the incomplete calendar month and must be excluded.

The source records should reproduce:
- September net revenue: $10,000,000.
- October net revenue: $9,000,000.
- Change: -$1,000,000.
- Percentage change: -10%.

These totals establish the size of the decline.
They do not establish customer churn as its cause.

## Proposed source-data contract

Use a small SQLite database populated from a versioned synthetic fixture.

Proposed table: revenue_transactions

| Column | Meaning |
| --- | --- |
| transaction_id | Unique synthetic record identifier |
| posting_date | ISO calendar date used for reporting |
| business_segment | Business segment, including Marketplace |
| entry_type | revenue or credit |
| amount_cents | Nonnegative integer amount in cents |
| currency | USD for this lesson |

Proposed calculation:
- Revenue entries contribute positive amounts.
- Credit entries subtract their amounts.
- Net revenue is revenue less credits.
- All amounts are USD; no currency conversion is implemented.
- Reporting follows posting_date, not invoice date or service date.
- Duplicate transaction identifiers are rejected.

These are demo business rules requiring review before implementation.
They are not claims about a real client's accounting policy.

## Fixture design

Include enough records to expose meaningful mistakes:
- Marketplace revenue and credits in September.
- Marketplace revenue and credits in October.
- November records that must be excluded.
- Another segment that must be excluded.
- Boundary-date records to test monthly filtering.
- A separate scenario whose records net to zero.
- A request with no matching records.

Keep the fixture small enough to reconcile manually.

Do not include customer activity or cancellation evidence that could
support a churn explanation in this lesson.

## Calculation rules

### Reporting periods

Derive the two most recent completed calendar months from the fixed date.
Use inclusive month starts and exclusive next-month starts.

Verify rollover across a year boundary in a focused test.

### Monetary calculations

Use integer cents for amounts and changes.

change_cents = current_cents - prior_cents

For a positive prior-period total:

change_pct = (current_cents - prior_cents) / prior_cents * 100

Use Decimal for percentage calculations and define explicit formatting.

Match the representation expected by Lesson 00 when constructing
compatible reference facts.

### Missing data and zero

- No matching records: report missing data, not zero revenue.
- Matching records that net to zero: report a genuine zero total.
- Zero prior-period total: percentage change is undefined.
- Negative prior-period total: document an explicit policy before
  implementation; do not silently apply a misleading percentage rule.

## Independent verification

Verify the reference facts using:
1. A SQL aggregation over the synthetic database.
2. A separately implemented Python reconciliation over the source fixture.
3. A small, manually inspectable expected-results table.

The Python reconciliation must not call the SQL aggregation or reuse
its calculated totals.

Both implementations will share the business specification, so agreement
does not prove the specification is correct. Manual inspection of the
fixture and expected totals remains part of the learning exercise.

Do not derive expected results from a future agent-generated answer
or from its generated SQL.

## Reference artifact

Create a separate Lesson 01 reference artifact rather than silently
overwriting Lesson 00's fixture.

Record:
- Case identifier and version.
- Synthetic dataset version.
- Fixed reporting date.
- Business-rule version.
- Expected scope, metric, periods, and amounts.
- Source-record identifiers or another reproducible evidence reference.
- Evidence limitation.
- Review status: demo_authored or pending_human_review.

Record actual human review only if it occurs.

The source database represents information a future agent may query.
The reference artifact belongs to the evaluator and must not be supplied
as an answer key to that agent.

## Proposed deliverables

Confirm exact paths against existing repository conventions.

- Versioned synthetic source fixture.
- Reusable database creation/loading code.
- SQL reference aggregation.
- Independent Python reconciliation.
- Versioned Lesson 01 reference artifact.
- Focused tests.
- `notebooks/01_reference_data.ipynb`.
- `docs/lessons/01_reference_data.md`.
- Updated lesson index.

Prefer generating the SQLite database from the fixture over committing
a binary database, unless repository conventions justify another choice.

## Acceptance criteria

| ID | Expected behavior | Verification |
| --- | --- | --- |
| AC01 | Database can be rebuilt deterministically | Rebuild and compare records/results |
| AC02 | Marketplace totals equal $10M and $9M | SQL, Python, and manual table agree |
| AC03 | November and other segments are excluded | Targeted fixture assertions |
| AC04 | Credits reduce net revenue | Focused calculation test |
| AC05 | Reporting periods use completed months | Boundary and year-rollover tests |
| AC06 | Missing records differ from genuine zero | Separate scenario assertions |
| AC07 | Zero denominator produces undefined percentage | Focused test |
| AC08 | Evidence does not establish churn | Inspect reference limitation and lesson explanation |
| AC09 | Reference records provenance and honest review status | Artifact assertions and review |
| AC10 | Lesson 00 behavior is preserved | Existing regression tests |
| AC11 | Notebook executes from a fresh kernel | Repository notebook runner |
| AC12 | Documentation matches implementation | Diff and example-output review |

AC08 checks how the limitation is represented in this lesson.
It is not a live semantic evaluation of an agent's answer.

## Exclusions

This lesson does not implement:
- Azure OpenAI calls.
- A live finance agent.
- MCP integration.
- Trajectory evaluation.
- An LLM judge.
- Production financial controls.
- Real client datasets.

## Implementation slices

### Slice 1: Source records and database

- Confirm schema and accounting conventions.
- Create the small fixture and manual reconciliation table.
- Implement deterministic database loading.
- Verify record identity, amounts, and rerun behavior.

### Slice 2: Reference calculation and verification

- Implement reporting-period selection.
- Implement SQL aggregation.
- Implement independent Python reconciliation.
- Cover filtering, credits, missing data, zero, and period boundaries.
- Produce and verify the reference artifact.

### Slice 3: Learning walkthrough

- Create the notebook.
- Create the companion lesson guide.
- Include a record-to-reference walkthrough.
- Explain why revenue change does not establish its cause.
- Execute checks and update the lesson index.

## Decisions requiring review

- Is posting_date the appropriate reporting basis for this demo?
- Is the revenue/credit sign convention sufficiently clear?
- What is the policy for negative prior-period revenue?
- Where should generated databases and execution artifacts live?
- How will the separate reference artifact remain compatible with
  Lesson 00 without changing its behavior?

## Progress

- [x] Repository inspected and prerequisite paths confirmed.
- [ ] Schema and business rules reviewed.
- [ ] Slice 1 implemented.
- [ ] Slice 1 verified.
- [ ] Slice 2 implemented.
- [ ] Slice 2 verified.
- [ ] Slice 3 implemented.
- [ ] Fresh-kernel notebook execution completed.
- [ ] Regression checks completed.
- [ ] Learner checkpoint completed.

## Verification log

No Lesson 01 implementation checks have been run.

Record actual commands and results here as work progresses.
Do not replace failures with a generic statement that validation passed.

## Decision log

No implementation decisions have been confirmed yet.

For each decision, record:
- Decision.
- Rationale.
- Any limitation or alternative left for later.

## Next action

Review the proposed transaction schema and accounting rules, then finalize
the scope of Slice 1 before implementation.
