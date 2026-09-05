# The fields we will receive in the transaction dictionary (all the raw fields from section 2 of the spec, plus is_clean, ml_score, rules_triggered, rules_verdict)
# The one field we are responsible for adding: final_decision

# decision_agent.py
#
# Receives a transaction dict that already contains:
#   transaction_id, sender_id, receiver_id, receiver_type, amount,
#   sender_balance_before, timestamp, is_clean, ml_score,
#   rules_triggered, rules_verdict
#
# Must return the same dict with one new field added:
#   final_decision  ("block", "flag", or "approve")

sample_transaction = {
    "transaction_id": "TXN10293",
    "sender_id": "USR001",
    "receiver_id": "USR045",
    "receiver_type": "internal",
    "amount": 50000,
    "sender_balance_before": 250000,
    "timestamp": "2026-08-16 14:00:00",
    "is_clean": True,
    "ml_score": 0.82,
    "rules_triggered": ["large_amount"],
    "rules_verdict": "flag",
}

# Placeholder threshold — chosen to match the example in the shared format spec.
# To be tuned later once we test the Pattern Spotting Agent's ml_score outputs
# against the labelled Kaggle dataset (see Chapter 4: Implementation and Testing).
ML_SCORE_THRESHOLD = 0.8

def make_decision(transaction):
    """
    Decision Agent.
    Combines ml_score (from Pattern Spotting Agent) and rules_verdict
    (from Rule Checking Agent) into one final_decision.
    """
    if "ml_score" not in transaction or "rules_verdict" not in transaction:
        raise ValueError(
            "Decision agent requires 'ml_score' and 'rules_verdict' to already "
            "be present in the transaction before this agent runs."
        )

    ml_score = transaction["ml_score"]
    rules_verdict = transaction["rules_verdict"]

    if rules_verdict not in ("block", "flag", "clear"):
        raise ValueError(
            f"Unexpected rules_verdict value: '{rules_verdict}'. "
            "Must be exactly one of 'block', 'flag', or 'clear'."
        )

    if rules_verdict == "block":
        final_decision = "block"

    elif rules_verdict == "flag":
        if ml_score > ML_SCORE_THRESHOLD:
            final_decision = "block"
        else:
            final_decision = "flag"

    else:  # rules_verdict == "clear"
        if ml_score > ML_SCORE_THRESHOLD:
            final_decision = "flag"
        else:
            final_decision = "approve"

    transaction["final_decision"] = final_decision
    return transaction

if __name__ == "__main__":
    test_cases = [
        {"ml_score": 0.9, "rules_verdict": "block", "expected": "block"},
        {"ml_score": 0.1, "rules_verdict": "block", "expected": "block"},
        {"ml_score": 0.9, "rules_verdict": "flag",  "expected": "block"},
        {"ml_score": 0.3, "rules_verdict": "flag",  "expected": "flag"},
        {"ml_score": 0.9, "rules_verdict": "clear", "expected": "flag"},
        {"ml_score": 0.2, "rules_verdict": "clear", "expected": "approve"},
    ]

    for case in test_cases:
        test_transaction = {
            "ml_score": case["ml_score"],
            "rules_verdict": case["rules_verdict"],
        }
        result = make_decision(test_transaction)
        actual = result["final_decision"]
        expected = case["expected"]
        status = "PASS" if actual == expected else "FAIL"
        print(f"{status}: ml_score={case['ml_score']}, rules_verdict={case['rules_verdict']} "
              f"-> got '{actual}', expected '{expected}'")