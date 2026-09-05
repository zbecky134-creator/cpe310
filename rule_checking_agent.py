# Threshold for a very large transaction
LARGE_AMOUNT_THRESHOLD = 100000


def check_blacklisted_account(transaction:dict, blacklist)->bool:
    """
    Checks whether the sender or receiver is blacklisted.
    """
    sender_id = transaction["sender_id"]
    receiver_id = transaction["receiver_id"]

    return sender_id in blacklist or receiver_id in blacklist


def check_large_amount(transaction)->bool:
    """
    Checks whether the transaction amount is
    N100,000 or more.
    """
    amount = int(transaction["amount"])

    return amount >= LARGE_AMOUNT_THRESHOLD


def check_account_fully_drained(transaction)->bool:
    """
    Checks whether the transaction uses the sender's
    entire available balance.
    """
    amount = transaction["amount"]
    balance = transaction["sender_balance_before"]

    return balance > 0 and amount == balance

def check_odd_hour_transaction(transaction):
    """
    Checks whether a transaction happened between
    12:00 AM and 5:00 AM.
    """
    time = int(transaction["timestamp"].split()[1].split(":")[0])

    return time == 0 or time <= 4




def rule_checking_agent(transaction, blacklist=None)->dict:
    """
    Applies fixed fraud-detection rules to a cleaned transaction.

    The function keeps all existing transaction fields unchanged
    and adds only:

        transaction["rules_triggered"]
        transaction["rules_verdict"]

    Possible verdicts:
        "block"
        "flag"
        "clear"
    """

    # If no blacklist is supplied, use an empty set
    if blacklist is None:
        blacklist = set()

    blacklist = set(blacklist)

    rules_triggered = []

    # Rule 1: Blacklisted account
    # Verdict: BLOCK
    if check_blacklisted_account(transaction, blacklist):
        rules_triggered.append("blacklisted_account")

    # Rule 2: Large amount
    # Verdict: FLAG
    if check_large_amount(transaction):
        rules_triggered.append("large_amount")
    
    # Rule 3: Account fully drained
    # Verdict: FLAG
    if check_account_fully_drained(transaction):
        rules_triggered.append("account_fully_drained")

    # Rule 4: Transaction at odd hours
    # Verdict: BLOCK
    if check_odd_hour_transaction(transaction):
        rules_triggered.append("odd_hour_transaction")

    # Determine rules verdict
    if "blacklisted_account" in rules_triggered or "odd_hour_transaction" in rules_triggered:
        rules_verdict = "block"
    elif rules_triggered:
        rules_verdict = "flag"
    else:
        rules_verdict = "clear"

    transaction["rules_triggered"] = rules_triggered
    transaction["rules_verdict"] = rules_verdict

    return transaction

if __name__ == "__main__":
    from pprint import pprint

    transaction = {
    "transaction_id": "TXN10293",
    "sender_id": "USR001",
    "receiver_id": "USR045",
    "receiver_type": "internal",   # "internal" or "external"
    "amount": 250000,
    "sender_balance_before": 250000,
    "timestamp": "2026-08-16 0:00:00"
    }


    pprint(rule_checking_agent(transaction))

    #Example ouput
    {'amount': 250000,
    'receiver_id': 'USR045',
    'receiver_type': 'internal',
    'rules_triggered': ['large_amount', 'account_fully_drained', 'odd_hour_transaction'],
    'rules_verdict': 'block',
    'sender_balance_before': 250000,
    'sender_id': 'USR001',
    'timestamp': '2026-08-16 0:00:00',
    'transaction_id': 'TXN10293'}