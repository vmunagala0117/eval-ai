# Lesson 01 — Build trustworthy reference data

> Why did Marketplace revenue decline last month?

A finance evaluator needs independently derived figures before it can grade
an answer. Lesson 00 supplied reference facts alongside authored candidates
and narrative reviews. Lesson 01 starts with source postings and derives
reference facts that can be reproduced. By the end, you should be able to
trace each figure back to the selected postings and explain what evidence
a causal claim would require. [Lesson 00](00_success_contract.md) ·
[Executable notebook](../../notebooks/01_reference_data.ipynb) ·
[Implementation plan](../plans/01_reference_data.md)

## 1. Inspect the source and schema

`load_revenue_transactions` validates and loads the synthetic v1 JSON
fixture into SQLite. The notebook displays the actual table schema with
`PRAGMA table_info` and lists every loaded record. [Loader](../../src/finance_evals/source_data.py) ·
[Source fixture](../../evals/source/revenue_transactions_v1.json)

| Column | SQLite type | Meaning |
| --- | --- | --- |
| `transaction_id` | TEXT | Unique primary key and evidence ID |
| `posting_date` | TEXT | Calendar date in YYYY-MM-DD format that determines the reporting period |
| `business_segment` | TEXT | Scope of the posting, such as Marketplace or Direct |
| `entry_type` | TEXT | `revenue` adds to net revenue and `credit` subtracts |
| `amount_cents` | INTEGER | Nonnegative magnitude in cents |
| `currency` | TEXT | USD throughout this fixture |

Integer cents retain exact monetary values. Divide by 100 for display in
dollars. A credit's stored magnitude is positive in this fixture and is
subtracted when computing net revenue.

| ID | Posting date | Segment | Entry type | Stored cents | Currency |
| --- | --- | --- | --- | ---: | --- |
| TX-001 | 2026-09-01 | Marketplace | revenue | 1,100,000,000 | USD |
| TX-002 | 2026-09-30 | Marketplace | credit | 100,000,000 | USD |
| TX-003 | 2026-10-01 | Marketplace | revenue | 950,000,000 | USD |
| TX-004 | 2026-10-31 | Marketplace | credit | 50,000,000 | USD |
| TX-005 | 2026-11-01 | Marketplace | revenue | 200,000,000 | USD |
| TX-006 | 2026-09-15 | Direct | revenue | 25,000,000 | USD |
| TX-007 | 2026-10-12 | Direct | revenue | 15,000,000 | USD |
| TX-008 | 2026-10-25 | Direct | credit | 15,000,000 | USD |

In a production evaluation, source ownership, snapshot version, reporting
policy, and data access would need to be established for the case. This
demo uses a versioned fixture and a fixed calendar reporting policy.

## 2. Select the completed months and source records

**Direct** and **Marketplace** are two business segments. In a Direct
sale, the company sells its own product or service, such as a subscription.
In a Marketplace sale, a third-party seller sells through the company's
platform, and the company might earn a fee. These examples illustrate the
labels. The synthetic fixture simply assigns each posting a
`business_segment`.

**Date filter.** As of November 18, 2026, the two most recent completed
calendar months are September and October. `completed_months` includes the
start date and excludes the end date of each range.

| Role | Inclusive start | Exclusive end | Marketplace IDs |
| --- | --- | --- | --- |
| Prior | 2026-09-01 | 2026-10-01 | TX-001, TX-002 |
| Current | 2026-10-01 | 2026-11-01 | TX-003, TX-004 |

The September 30 credit (TX-002) is part of September. The October 1
revenue (TX-003) and October 31 credit (TX-004) are both part of October.
The $2 million Marketplace posting on November 1 (TX-005) falls in
November, which is still in progress on the reporting date.

**Segment filter.** The question asks about Marketplace revenue, so only
Marketplace postings within those dates count. Including September's
Direct posting (TX-006) would overstate Marketplace revenue by $250,000.
In October, Direct has $150,000 in revenue (TX-007) and $150,000 in credits
(TX-008), for a net of $0. Including both would still produce a $9 million
net total, but the transaction count would rise from two to four and the
evidence would include two Direct IDs. The lesson checks the total, the
count, and the IDs to verify which postings contributed.

## 3. Verify SQL against Python and manual expectations

`aggregate_revenue_sql` queries SQLite with bound values for segment,
currency, and date range. `reconcile_revenue_python` reads the original
JSON and separately filters, counts, totals, and sorts the contributing
IDs. The notebook compares both methods against these manual values and
the expected IDs from the period table. [Calculation code](../../src/finance_evals/reference_calculations.py)

| Period | Count | Revenue cents | Credit cents | Net cents | Net dollars |
| --- | ---: | ---: | ---: | ---: | ---: |
| September | 2 | 1,100,000,000 | 100,000,000 | 1,000,000,000 | $10,000,000 |
| October | 2 | 950,000,000 | 50,000,000 | 900,000,000 | $9,000,000 |

The signed difference is **−100,000,000 cents (−$1,000,000)**.
`compare_revenue` divides the difference by the positive prior total,
multiplies by 100, and uses Decimal with two decimal places and ties
rounded away from zero. The result is stored as `"-10.00"`.

The two implementations share fixture validation and apply the same
business rules. Agreement helps catch errors in the separate
implementations. A shared misunderstanding of the reporting policy can
still yield agreement, which is why the notebook checks the date bounds
and compares against manually selected rows and totals.

## 4. Distinguish zero from missing data

| October query | Matching postings | Revenue | Credits | Net revenue | Evidence IDs |
| --- | ---: | ---: | ---: | ---: | --- |
| Direct | 2 | $150,000 | $150,000 | $0 | TX-007, TX-008 |
| Wholesale | 0 | `None` | `None` | `None` | `()` |

`record_count` counts postings that match the filters. No posting in the
fixture uses the Wholesale label, so that query matches zero rows. A
segment with postings in other months and none in October would give
the same October result. For Direct, the two amounts offset each other,
so the matching records establish a genuine zero.

### Compare two months

The first row uses Direct's actual September and October results. The
other rows illustrate comparison inputs in dollars. The code uses cents.

| Scenario | Prior net | Current net | Signed change | Stored percentage | Reason |
| --- | ---: | ---: | ---: | --- | --- |
| Direct, September to October | $250,000 | $0 | −$250,000 | `"-100.00"` | — |
| Zero prior net | $0 | $50,000 | +$50,000 | `None` | Prior net revenue is zero. |
| Negative prior net | −$20,000 | $50,000 | +$70,000 | `None` | Prior net revenue is negative. |
| Missing current month | $250,000 | `None` | `None` | `None` | Missing revenue in one or both periods. |

The signed change is current net revenue minus prior net revenue. When
the prior net is positive, percentage change divides that difference by
the prior net and multiplies by 100. The code stores the percentage as a
string rounded to two decimal places, with ties rounded away from zero.

- **Zero prior net.** Going from $0 to $50,000 gives a $50,000 increase.
  Dividing by zero is undefined, so the percentage is `None`.
- **Negative prior net.** Going from −$20,000 to $50,000 gives a $70,000
  increase. Dividing by −$20,000 and multiplying by 100 gives −350%,
  which reads like a decline. The lesson's reporting rule returns
  `None` for the percentage and keeps the $70,000 increase.
- **Missing either month.** The calculation needs both net amounts to
  subtract, so both change fields are `None`.

## 5. Validate the artifact and apply the Lesson 00 contract

The nested `reference` contains the scope, metric, period labels,
integer-cent amounts, and percentage string used by `evaluate`. Outer
metadata records the case, dataset, and business-rule versions, the
fixed date, source fixture, contributing IDs, evidence limitation,
and `demo_authored` review status. The notebook runs the existing generator
without `--write` and compares its verified JSON with the stored file.
The artifact is evaluator-owned. [Reference artifact](../../evals/reference/lesson01_marketplace_revenue_v1.json) ·
[Reference generator](../../scripts/generate_lesson01_reference.py)

The notebook inspects `evaluate` and the two candidate narratives and
reviews before matching them by ID and passing them to the evaluator.
The evaluator checks the review against the exact narrative.
[Evaluator](../../src/finance_evals/contracts.py) ·
[Candidates](../../evals/cases/lesson00_answers.json) ·
[Authored reviews](../../evals/reviews/lesson00_reviews.json)

| Candidate | Numbers | Scope and periods | Authored narrative verdict | Overall |
| --- | --- | --- | --- | --- |
| `limited_evidence` | pass | pass | pass | pass |
| `unsupported_churn` | pass | pass | fail | fail |

The numerical reference now traces back to source postings. Narrative
verdicts still come from supplied authored reviews. The demonstration
runs offline with no live agent or LLM judge.

## 6. Verify and interpret the limits

Use the project environment from the repository root. [Environment setup](../setup.md)

```bash
python -m pytest -q
python scripts/run_notebooks.py
```

The runner executes both notebooks in fresh kernels and saves their
executed copies under `reports/executed/`. In Lesson 01, look for the
matching SQL and Python tables, the zero and missing result structures,
the verified artifact, and overall verdicts of `pass` and `fail`.

The postings explain the arithmetic behind the decline. Investigating
churn would require customer-level activity or cancellations linked to
the revenue change. The USD-only sample also leaves currency conversion
and other reporting policies outside the demonstration.

## 7. Check your understanding

1. Which records contribute to each month, and why would including the
   two offsetting Direct records still invalidate the Marketplace evidence?
2. Which result fields distinguish a genuine zero from a missing period,
   and how does each affect a percentage comparison?
3. Why do both authored candidates pass the numbers check while only one
   passes overall? What evidence would support a churn explanation?

Lesson 02 plans to run a finance agent against source data and capture
its tool results and trace for evaluation. [Lesson index](README.md)
