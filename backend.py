from flask import Flask, request, jsonify
from uuid import uuid4
from datetime import datetime, timedelta
from collections import defaultdict
import threading

app = Flask(_name_)

# In-memory data stores
users = {}
balances = defaultdict(float)
transactions = defaultdict(list)
request_log = defaultdict(list)
lock = threading.Lock()

# Rate limiting and fraud detection config
MAX_REQUESTS_PER_MINUTE = 10
TRANSFER_LIMIT = 1000  # Max amount per transfer

# Helper functions
def current_time():
    return datetime.utcnow()

def is_rate_limited(user_id):
    now = current_time()
    one_minute_ago = now - timedelta(minutes=1)
    request_log[user_id] = [t for t in request_log[user_id] if t > one_minute_ago]
    return len(request_log[user_id]) >= MAX_REQUESTS_PER_MINUTE


def log_request(user_id):
    request_log[user_id].append(current_time())


def record_transaction(user_id, action, amount, target_id=None):
    transactions[user_id].append({
        'timestamp': current_time().isoformat(),
        'action': action,
        'amount': amount,
        'target': target_id
    })


# Routes
@app.route('/register', methods=['POST'])
def register():
    user_id = str(uuid4())
    with lock:
        users[user_id] = {'id': user_id, 'created_at': current_time().isoformat()}
    return jsonify({'message': 'User registered', 'user_id': user_id}), 201


@app.route('/deposit', methods=['POST'])
def deposit():
    data = request.json
    user_id = data.get('user_id')
    amount = float(data.get('amount', 0))

    if user_id not in users or amount <= 0:
        return jsonify({'error': 'Invalid user or amount'}), 400

    if is_rate_limited(user_id):
        return jsonify({'error': 'Rate limit exceeded'}), 429

    with lock:
        balances[user_id] += amount
        log_request(user_id)
        record_transaction(user_id, 'deposit', amount)

    return jsonify({'message': 'Deposit successful', 'balance': balances[user_id]}), 200


@app.route('/withdraw', methods=['POST'])
def withdraw():
    data = request.json
    user_id = data.get('user_id')
    amount = float(data.get('amount', 0))

    if user_id not in users or amount <= 0:
        return jsonify({'error': 'Invalid user or amount'}), 400

    if is_rate_limited(user_id):
        return jsonify({'error': 'Rate limit exceeded'}), 429

    with lock:
        if balances[user_id] < amount:
            return jsonify({'error': 'Insufficient funds'}), 400
        balances[user_id] -= amount
        log_request(user_id)
        record_transaction(user_id, 'withdraw', amount)

    return jsonify({'message': 'Withdrawal successful', 'balance': balances[user_id]}), 200


@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.json
    sender_id = data.get('sender_id')
    recipient_id = data.get('recipient_id')
    amount = float(data.get('amount', 0))

    if sender_id not in users or recipient_id not in users or sender_id == recipient_id or amount <= 0:
        return jsonify({'error': 'Invalid transfer details'}), 400

    if amount > TRANSFER_LIMIT:
        return jsonify({'error': 'Transfer amount exceeds allowed limit'}), 403

    if is_rate_limited(sender_id):
        return jsonify({'error': 'Rate limit exceeded'}), 429

    with lock:
        if balances[sender_id] < amount:
            return jsonify({'error': 'Insufficient funds'}), 400
        balances[sender_id] -= amount
        balances[recipient_id] += amount
        log_request(sender_id)
        record_transaction(sender_id, 'transfer_out', amount, recipient_id)
        record_transaction(recipient_id, 'transfer_in', amount, sender_id)

    return jsonify({'message': 'Transfer successful', 'balance': balances[sender_id]}), 200


@app.route('/balance/<user_id>', methods=['GET'])
def get_balance(user_id):
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'balance': balances[user_id]}), 200


@app.route('/transactions/<user_id>', methods=['GET'])
def get_transactions(user_id):
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'transactions': transactions[user_id]}), 200


if _name_ == '_main_':
    app.run(debug=True)