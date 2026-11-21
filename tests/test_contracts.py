import json
from pathlib import Path
from copy import deepcopy
from finance_evals.contracts import evaluate, percentage_change
ROOT = Path(__file__).resolve().parents[1]
REF = json.loads((ROOT / "evals/reference/revenue_case.json").read_text())["reference"]
ANS = json.loads((ROOT / "evals/cases/lesson00_answers.json").read_text())
REV = json.loads((ROOT / "evals/reviews/lesson00_reviews.json").read_text())

def test_supported_answer_passes():
    assert evaluate(ANS[0], REF, REV[0])["overall"] == "pass"

def test_correct_numbers_do_not_override_unsupported_cause():
    result = evaluate(ANS[1], REF, REV[1])
    assert result["checks"]["numbers_correct"] == "pass"
    assert result["overall"] == "fail"

def test_wrong_period_fails():
    assert evaluate(ANS[2], REF, REV[2])["checks"]["scope_and_period_correct"] == "fail"

def test_missing_review_is_unverifiable():
    assert evaluate(ANS[0], REF)["overall"] == "unverifiable"

def test_edited_narrative_invalidates_review():
    changed = dict(ANS[0], narrative="Revenue rose 20%.")
    assert evaluate(changed, REF, REV[0])["checks"]["claims_supported"] == "unverifiable"

def test_wrong_number_fails():
    changed = dict(ANS[0], change_cents=100000000)
    assert evaluate(changed, REF, REV[0])["checks"]["numbers_correct"] == "fail"

def test_percentage_and_zero_denominator():
    assert percentage_change(900, 1000) == -10
    assert percentage_change(900, 0) is None
