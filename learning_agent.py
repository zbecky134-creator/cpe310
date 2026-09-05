# learning_agent.py
#
# LEARNING AGENT — standalone version
# Agent-Based Financial Fraud Detection and Prevention System
#
# Role in the pipeline:
#   The learning agent doesn't sit in the per-transaction pipeline
#   like the other five. It runs periodically on a BATCH of
#   already-decided transactions (output of the Decision Agent),
#   compares each final_decision against the transaction's true label
#   (fraud / not fraud, taken from the Kaggle dataset), and works out
#   how the system's threshold should shift to improve.
#
#   For this project, "improve the system" means: recommend a new
#   ML_SCORE_THRESHOLD value that the Decision Agent should switch to
#   next time, based on how many false alarms vs missed fraud cases
#   showed up in the batch. A live, continuously retraining model is
#   out of scope — demonstrating one adjustment pass on held-out data
#   is enough to prove the concept (per the project guide, section 2.6).
#
# Input this agent expects:
#   A batch (list) of transaction dicts, each already carrying the
#   fields the Decision Agent produces:
#       ml_score, rules_verdict, final_decision  ("block"/"flag"/"approve")
#   plus one ground-truth field this agent relies on:
#       actual_fraud   (True/False — the real Kaggle label)
#
# Output this agent produces:
#   A report dict: confusion counts, false positive/negative rates,
#   and a recommended new ML_SCORE_THRESHOLD.
#
# This file does NOT import decision_agent.py or anything else from
# the team. It only needs whatever transaction batch the Decision
# Agent already produced — hand it that, and it runs on its own.


CURRENT_ML_SCORE_THRESHOLD = 0.8  # whatever the Decision Agent is using right now


# ---------------------------------------------------------------------
# 1. EVALUATE A BATCH OF DECIDED TRANSACTIONS
# ---------------------------------------------------------------------
def evaluate_batch(decided_transactions):
    """
    Compares final_decision against actual_fraud for every transaction
    in the batch and returns confusion-matrix-style counts.

    A transaction counts as "flagged" if final_decision is
    'block' or 'flag' (either one interrupts a normal transaction).
    'approve' counts as "cleared".
    """
    true_positive = 0   # flagged, and it really was fraud
    false_positive = 0  # flagged, but it was actually normal
    true_negative = 0   # cleared, and it really was normal
    false_negative = 0  # cleared, but it was actually fraud

    for txn in decided_transactions:
        flagged = txn["final_decision"] in ("block", "flag")
        actually_fraud = txn["actual_fraud"]

        if flagged and actually_fraud:
            true_positive += 1
        elif flagged and not actually_fraud:
            false_positive += 1
        elif not flagged and not actually_fraud:
            true_negative += 1
        else:
            false_negative += 1

    total = len(decided_transactions)
    return {
        "total": total,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "true_negative": true_negative,
        "false_negative": false_negative,
        "false_positive_rate": round(false_positive / total, 3) if total else 0,
        "false_negative_rate": round(false_negative / total, 3) if total else 0,
    }


# ---------------------------------------------------------------------
# 2. ADJUST THE THRESHOLD BASED ON THE EVALUATION
# ---------------------------------------------------------------------
def recommend_threshold(current_threshold, metrics, step=0.05):
    """
    Simple, explainable adjustment rule:
      - too many false alarms (false_positive_rate too high)
            -> raise the threshold, make it harder to flag/block
      - too much fraud slipping through (false_negative_rate too high)
            -> lower the threshold, make it easier to flag/block
      - both are low -> leave it alone

    The 0.1 tolerance below is a placeholder; in Chapter 4 this should
    be justified against the Kaggle dataset's actual score spread.
    """
    fpr = metrics["false_positive_rate"]
    fnr = metrics["false_negative_rate"]
    new_threshold = current_threshold

    if fpr > 0.1 and fpr >= fnr:
        new_threshold = round(min(current_threshold + step, 1.0), 3)
        reason = f"false positive rate {fpr} is too high raising threshold to catch fewer normal transactions"
    elif fnr > 0.1 and fnr > fpr:
        new_threshold = round(max(current_threshold - step, 0.0), 3)
        reason = f"false negative rate {fnr} is too high lowering threshold to catch more fraud"
    else:
        reason = "false positive and false negative rates are both acceptable no change made"

    return new_threshold, reason


# ---------------------------------------------------------------------
# 3. RUN ONE FULL LEARNING PASS
# ---------------------------------------------------------------------
def learning_agent(batch, current_threshold):
    """
    Full cycle: evaluate the batch under the current threshold, then
    recommend an adjusted threshold for next time.
    """
    metrics = evaluate_batch(batch)
    new_threshold, reason = recommend_threshold(current_threshold, metrics)

    return {
        "evaluated_on": metrics["total"],
        "metrics": metrics,
        "old_threshold": current_threshold,
        "new_threshold": new_threshold,
        "reason": reason,
    }


# ---------------------------------------------------------------------
# 4. DEMO RUN — a held-out batch, standing in for what the
#    Decision Agent would have already handed off
# ---------------------------------------------------------------------
if __name__ == "__main__":
    import json

    # Each transaction here already has final_decision filled in —
    # exactly what this agent would receive from the Decision Agent
    # in the real pipeline. actual_fraud is the ground-truth label
    # that would come from the Kaggle dataset.
    decided_batch = [
        {"ml_score": 0.92, "rules_verdict": "flag",  "final_decision": "block",   "actual_fraud": True},
        {"ml_score": 0.55, "rules_verdict": "clear", "final_decision": "approve", "actual_fraud": False},
        {"ml_score": 0.88, "rules_verdict": "clear", "final_decision": "flag",    "actual_fraud": False},  # false alarm
        {"ml_score": 0.83, "rules_verdict": "clear", "final_decision": "flag",    "actual_fraud": False},  # false alarm
        {"ml_score": 0.15, "rules_verdict": "clear", "final_decision": "approve", "actual_fraud": False},
        {"ml_score": 0.20, "rules_verdict": "block", "final_decision": "block",   "actual_fraud": True},
        {"ml_score": 0.10, "rules_verdict": "clear", "final_decision": "approve", "actual_fraud": True},   # missed fraud
        {"ml_score": 0.60, "rules_verdict": "clear", "final_decision": "approve", "actual_fraud": False},
        {"ml_score": 0.81, "rules_verdict": "clear", "final_decision": "flag",    "actual_fraud": False},  # false alarm
        {"ml_score": 0.05, "rules_verdict": "clear", "final_decision": "approve", "actual_fraud": False},
    ]

    report = learning_agent(decided_batch, CURRENT_ML_SCORE_THRESHOLD)
    print("=== LEARNING AGENT REPORT ===")
    print(json.dumps(report, indent=2))
