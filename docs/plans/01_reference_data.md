# Lesson 01: Building trustworthy reference data

Status: All three slices are implemented and verified. The learner checkpoint is complete.

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

## Source-data contract

Use a small SQLite database populated from a versioned synthetic fixture.

The SQLite table is `revenue_transactions`.

| Column | Meaning |
| --- | --- |
| transaction_id | Unique synthetic record identifier |
| posting_date | ISO calendar date used for reporting |
| business_segment | Business segment, including Marketplace |
| entry_type | revenue or credit |
| amount_cents | Nonnegative integer amount in cents |
| currency | USD for this lesson |

Reporting rules for Slice 2:
- Revenue entries contribute positive amounts.
- Credit entries subtract their amounts.
- Net revenue is revenue less credits.
- All amounts are USD; no currency conversion is implemented.
- Reporting follows posting_date, not invoice date or service date.
- Duplicate transaction identifiers are rejected.

These rules apply to the synthetic demo.

## Fixture design

The [v1 fixture](../../evals/source/revenue_transactions_v1.json) contains
eight synthetic transactions. The amounts below show their contribution
under the reporting rules. Credits are stored as nonnegative cents.

| Record | Posting date | Segment | Entry type | Signed USD | Scenario |
| --- | --- | --- | --- | ---: | --- |
| TX-001 | 2026-09-01 | Marketplace | Revenue | +$11,000,000 | September start |
| TX-002 | 2026-09-30 | Marketplace | Credit | −$1,000,000 | September end |
| TX-003 | 2026-10-01 | Marketplace | Revenue | +$9,500,000 | October start |
| TX-004 | 2026-10-31 | Marketplace | Credit | −$500,000 | October end |
| TX-005 | 2026-11-01 | Marketplace | Revenue | +$2,000,000 | Incomplete month |
| TX-006 | 2026-09-15 | Direct | Revenue | +$250,000 | September segment exclusion |
| TX-007 | 2026-10-12 | Direct | Revenue | +$150,000 | October zero-net scenario |
| TX-008 | 2026-10-25 | Direct | Credit | −$150,000 | October zero-net scenario |

| Scope and period | Contributing records | Manual arithmetic | Expected net revenue |
| --- | --- | --- | ---: | ---: |
| Marketplace, September 2026 | TX-001, TX-002 | $11,000,000 − $1,000,000 | $10,000,000 |
| Marketplace, October 2026 | TX-003, TX-004 | $9,500,000 − $500,000 | $9,000,000 |
| Direct, October 2026 | TX-007, TX-008 | $150,000 − $150,000 | $0 |
| Wholesale, October 2026 | None | No matching records | Missing |

The fixture contains posting records only, so it cannot establish whether
customer churn caused the decline.

### Loading and reruns

`load_revenue_transactions(connection, fixture_path)` validates the JSON
fixture before writing and creates and populates the table atomically.
It requires the six schema fields, unique nonblank IDs, nonblank segments,
canonical calendar dates, supported entry types, USD currency, and
nonnegative JSON integers in SQLite's signed 64-bit range.

The caller owns the SQLite connection and any surrounding transaction.
A load into an existing `revenue_transactions` table fails without
changing its rows. Rebuild against a fresh database for an identical
set of records. Use an in-memory connection or a new local
`*.sqlite3` file, which Git ignores along with its sidecars.

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

Calculate percentages with Decimal at 64-digit precision. Round to two
decimal places using ROUND_HALF_UP (ties away from zero), and format the
result as a string with two decimal places and no percent sign.

Match the representation expected by Lesson 00 when constructing
compatible reference facts.

### Missing data and zero

- No matching records: report missing data, not zero revenue.
- Matching records that net to zero: report a genuine zero total.
- Zero or negative prior-period total: retain the signed cent change and
  return an undefined percentage with a reason specific to zero or negative.
- Either period missing: both change fields are unavailable and the result
  includes a missing-data reason. A genuine zero current total is valid.

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

The [Lesson 01 reference artifact](../../evals/reference/lesson01_marketplace_revenue_v1.json)
is versioned separately from Lesson 00's fixture. Its nested reference
fields use Lesson 00's existing field names and types. Missing-data
and nonpositive-prior scenarios are covered in tests outside this artifact.

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

## Deliverables

- Versioned synthetic source fixture.
- Reusable database creation/loading code.
- SQL reference aggregation.
- Independent Python reconciliation.
- Versioned Lesson 01 reference artifact.
- Focused tests.
- `notebooks/01_reference_data.ipynb`.
- `docs/lessons/01_reference_data.md`.
- Updated lesson index.

### Slice 1 files created

- [Versioned source fixture](../../evals/source/revenue_transactions_v1.json)
- [SQLite schema and loader](../../src/finance_evals/source_data.py)
- [Loader tests](../../tests/test_source_data.py)

The manual reconciliation is in this plan. The repository's
[ignore rules](../../.gitignore) cover generated SQLite files.

### Slice 2 files created

- [Period selection, SQL aggregation, Python reconciliation, and comparison](../../src/finance_evals/reference_calculations.py)
- [Explicit reference generator](../../scripts/generate_lesson01_reference.py)
- [Versioned evaluator-only reference](../../evals/reference/lesson01_marketplace_revenue_v1.json)
- [Calculation and artifact tests](../../tests/test_reference_calculations.py)

The existing [fixture loader](../../src/finance_evals/source_data.py)
now exposes its fixture reader so both calculation paths use the same
source validation. The Python calculation reads the JSON and filters,
totals, and collects IDs independently of SQLite.

Run the generator with `--write` to update the artifact after the explicit
manual checks pass. With no flag it prints verified JSON. Tests compare
that output with the checked-in artifact without writing to it.

SQLite aggregates and collects evidence in one query. Its integer
SUM requires the scoped revenue and credit subtotals each to fit in a
signed 64-bit integer. The small synthetic fixture is within that range.

### Slice 3 files created

- [Executable notebook](../../notebooks/01_reference_data.ipynb)
- [Companion guide](../lessons/01_reference_data.md)

The [lesson index](../lessons/README.md) links to the guide and records
Lesson 01 as implemented offline.

## Acceptance criteria

| ID | Expected behavior | Verification |
| --- | --- | --- |
| AC01 | Database can be rebuilt deterministically | Rebuild and compare records/results |
| AC02 | Marketplace totals equal $10M and $9M | SQL, Python, and manual table agree |
| AC03 | November and other segments are excluded | Targeted fixture assertions |
| AC04 | Credits reduce net revenue | Focused calculation test |
| AC05 | Reporting periods use completed months | Boundary and year-rollover tests |
| AC06 | Missing records differ from genuine zero | Separate scenario assertions |
| AC07 | Zero or negative prior revenue produces undefined percentage with a reason | Focused tests |
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

## Progress

- [x] Repository inspected and prerequisite paths confirmed.
- [x] Schema and demo business rules confirmed for Slice 1.
- [x] Slice 1 implemented.
- [x] Slice 1 verified.
- [x] Slice 2 implemented.
- [x] Slice 2 verified.
- [x] Slice 3 implemented.
- [x] Fresh-kernel notebook execution completed for Lessons 00 and 01.
- [x] Lesson 00 and Slice 1 regression tests passed for Slice 2.
- [x] Learner checkpoint completed through discussion.

### Learner checkpoint discussion

The learner confirmed completion through discussion and demonstrated
these concepts:

- A matching total cannot validate out-of-scope evidence. The contributing
  records must also match the question's scope.
- A period with no matching records represents missing data. A genuine
  zero requires matching records whose amounts net to zero.
- A churn explanation requires relevant, traceable evidence linking churn
  to the revenue change. Mentioning churn alone provides insufficient support.

## Verification log

- Git checkpoint: `.venv/bin/python -m pytest -q` passed all 35 tests.
  `.venv/bin/python scripts/run_notebooks.py` executed both notebooks in
  fresh kernels. Lesson 00 ran with its existing local edits, which are
  excluded from the Lesson 01 commit. The reference check ran without
  rewriting the artifact.

- Expanded the companion guide and notebook with October evidence and
  month-over-month comparison tables. All 35 tests passed. The notebook
  runner executed Lessons 00 and 01 in fresh kernels after the comparison
  table formatter was updated to handle missing values.

- Companion guide clarification: verified the posting dates, segments,
  and amounts against the fixture and checked the filters against the
  calculation code. `.venv/bin/python -m pytest -q` passed all 35 tests.

- `.venv/bin/python -m pytest -q` on Python 3.12.3 passed all 22
  tests, including seven Lesson 00 regression tests. The loader tests
  check persisted values, rejected inputs, equal rows from fresh rebuilds,
  and preservation of an existing table on rerun.
- `git check-ignore evals/source/generated.sqlite3 evals/source/generated.sqlite3-wal`
  confirmed Git ignores both paths.
- Before Slice 2, `.venv/bin/python -m pytest -q` passed all 22 existing tests.
- `.venv/bin/python scripts/generate_lesson01_reference.py --write` generated
  the artifact after SQL, Python, and manual values agreed on the period
  totals and IDs, and the comparison matched the expected cents and percentage.
- After Slice 2, `.venv/bin/python -m pytest -q` on Python 3.12.3 passed
  all 35 tests, including all 22 existing tests. The new tests verify
  period boundaries, signed arithmetic, evidence IDs, missing and zero
  behavior, rounding, and reproducible artifact output.
- Slice 3: `.venv/bin/python -m pytest -q` passed all 35 tests.
- `.venv/bin/python scripts/run_notebooks.py` initially failed in the
  sandbox when Jupyter tried to open a kernel socket. The approved rerun
  executed both notebooks in fresh kernels and saved outputs under
  `reports/executed/`. Lesson 01 confirmed the reconciliation, validated
  the stored artifact, and produced the expected `pass` and `fail` verdicts.
- Local documentation and notebook links resolved, and `git diff --check`
  passed. Hash checks confirmed the pre-existing Lesson 00 notebook edits
  and the reference artifact were preserved byte for byte. The learner
  checkpoint was still open at the end of Slice 3 verification.

## Decision log

- Use `posting_date` as the calendar reporting basis. The fixture includes
  month-start and month-end postings to expose boundary errors.
- Store nonnegative integer cents in USD. Use `entry_type` to determine
  the sign for reporting, so records retain their original magnitudes
  and credits subtract consistently.
- Report an undefined percentage with an explicit reason when prior
  revenue is zero or negative. This avoids a division by zero or an
  ambiguous percentage based on a negative starting value. Keep the
  signed cent change for those cases when both periods have data.
- Rebuild SQLite from the versioned JSON fixture. Use fresh databases
  for repeatable loads and reject a second load into an existing table
  to preserve its contents.
- Use Direct for both segment exclusion and the zero-net case to keep the
  fixture small. Use absent Wholesale activity for the missing-data case.

- Return a zero count, empty evidence IDs, and absent totals for missing
  periods. The zero-net scenario has a positive count and valid zero cents.
- Sort the transaction IDs for stable evidence and generate the artifact
  explicitly only after SQL and Python match the manual reconciliation.
  The reference remains evaluator-owned and demo-authored.

- The walkthrough uses disposable in-memory databases and calls the
  existing artifact generator in stdout mode to check the stored JSON.
  Its narrative checks reuse the authored reviews from Lesson 00.

## Next action

Lesson 02 plans to run a finance
agent against source data and capture its tool results and trace.
The Lesson 01 fixture supports reconciliation of the amount of the
decline. Investigating its cause requires additional evidence, such as
customer activity or cancellation records tied to revenue changes.
