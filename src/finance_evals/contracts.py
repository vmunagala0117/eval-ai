"""Lesson 00: inspect arithmetic separately from supplied narrative reviews.

This is not an automated natural-language grounding evaluator.
"""
from decimal import Decimal

def evaluate(answer, reference, narrative_review=None):
    fields = ("prior_cents", "current_cents", "change_cents", "change_pct")
    numbers_ok = all(type(answer.get(k)) is type(reference[k]) and answer[k] == reference[k] for k in fields)
    scope_ok = all(answer.get(k) == reference[k] for k in ("scope", "metric", "prior_period", "current_period"))
    review_ok = (
        isinstance(narrative_review, dict)
        and narrative_review.get("answer_id") == answer.get("id")
        and narrative_review.get("narrative") == answer.get("narrative")
        and narrative_review.get("verdict") in ("pass", "fail")
        and bool(narrative_review.get("reason"))
    )
    grounding = narrative_review["verdict"] if review_ok else "unverifiable"
    checks = {
        "numbers_correct": "pass" if numbers_ok else "fail",
        "scope_and_period_correct": "pass" if scope_ok else "fail",
        "claims_supported": grounding,
    }
    overall = "fail" if "fail" in checks.values() else ("pass" if all(v == "pass" for v in checks.values()) else "unverifiable")
    return {"answer_id": answer.get("id"), "checks": checks, "overall": overall,
            "review_reason": narrative_review["reason"] if review_ok else "No valid review tied to this exact narrative",
            "mode": "offline_authored_examples"}

def percentage_change(current_cents, prior_cents):
    if prior_cents <= 0:
        return None
    return Decimal(current_cents - prior_cents) / Decimal(prior_cents) * 100
