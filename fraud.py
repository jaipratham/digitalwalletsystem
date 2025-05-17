import time
from collections import defaultdict

# Track user actions in-memory for demo purposes
user_transfer_logs = defaultdict(list)

# Configurable thresholds
MAX_TRANSFERS_PER_MINUTE = 5
LARGE_WITHDRAWAL_THRESHOLD = 10000  # e.g., $10,000

def log_transfer(user_id, amount):
    timestamp = time.time()
    user_transfer_logs[user_id].append(timestamp)
    # Keep only recent entries (last 60 seconds)
    user_transfer_logs[user_id] = [
        ts for ts in user_transfer_logs[user_id] if timestamp - ts < 60
    ]
    if len(user_transfer_logs[user_id]) > MAX_TRANSFERS_PER_MINUTE:
        print(f"[FRAUD] User {user_id} flagged: too many transfers in 1 minute.")
        return "rate_limit_exceeded"
    return None

def check_large_withdrawal(amount):
    if amount >= LARGE_WITHDRAWAL_THRESHOLD:
        print(f"[FRAUD] Large withdrawal detected: ${amount}")
        return "large_withdrawal"
    return None
