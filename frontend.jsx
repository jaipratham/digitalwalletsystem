import React, { useState } from 'react';
import axios from 'axios';

export default function WalletApp() {
  const [userId, setUserId] = useState('');
  const [amount, setAmount] = useState('');
  const [recipientId, setRecipientId] = useState('');
  const [balance, setBalance] = useState(null);
  const [transactions, setTransactions] = useState([]);

  const API_BASE = 'http://localhost:5000';

  const register = async () => {
    const res = await axios.post(${API_BASE}/register);
    setUserId(res.data.user_id);
    alert('User registered: ' + res.data.user_id);
  };

  const deposit = async () => {
    await axios.post(${API_BASE}/deposit, { user_id: userId, amount });
    fetchBalance();
  };

  const withdraw = async () => {
    await axios.post(${API_BASE}/withdraw, { user_id: userId, amount });
    fetchBalance();
  };

  const transfer = async () => {
    await axios.post(${API_BASE}/transfer, {
      sender_id: userId,
      recipient_id: recipientId,
      amount
    });
    fetchBalance();
  };

  const fetchBalance = async () => {
    const res = await axios.get(${API_BASE}/balance/${userId});
    setBalance(res.data.balance);
  };

  const fetchTransactions = async () => {
    const res = await axios.get(${API_BASE}/transactions/${userId});
    setTransactions(res.data.transactions);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">
    <div className="w-full max-w-2xl bg-white shadow-lg rounded-xl p-6">
      <h1 className="text-3xl font-semibold text-center text-blue-700 mb-6">💰 Digital Wallet</h1>

      <div className="space-y-6">
        {/* Register Section */}
        <div>
          <button onClick={register} className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium transition">
            Register New User
          </button>
          <p className="mt-2 text-sm text-gray-600 text-center">User ID: <code className="text-gray-800">{userId}</code></p>
        </div>

        {/* Amount Section */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <input
            type="number"
            placeholder="Amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="col-span-1 sm:col-span-1 border border-gray-300 p-2 rounded-lg"
          />
          <button onClick={deposit} className="bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg transition">
            Deposit
          </button>
          <button onClick={withdraw} className="bg-yellow-500 hover:bg-yellow-600 text-white py-2 rounded-lg transition">
            Withdraw
          </button>
        </div>

        {/* Transfer Section */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="Recipient ID"
            value={recipientId}
            onChange={(e) => setRecipientId(e.target.value)}
            className="col-span-1 sm:col-span-2 border border-gray-300 p-2 rounded-lg"
          />
          <button onClick={transfer} className="bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-lg transition">
            Transfer
          </button>
        </div>

        {/* Balance Section */}
        <div className="flex items-center justify-between gap-4">
          <button onClick={fetchBalance} className="bg-gray-800 hover:bg-gray-900 text-white py-2 px-4 rounded-lg transition w-full">
            Get Balance
          </button>
          {balance !== null && (
            <div className="text-center text-lg text-gray-700 font-semibold w-full">
              Balance: ${balance.toFixed(2)}
            </div>
          )}
        </div>

        {/* Transactions Section */}
        <div>
          <button onClick={fetchTransactions} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg transition mb-3">
            View Transactions
          </button>
          <ul className="space-y-2 max-h-60 overflow-y-auto">
            {transactions.map((tx, index) => (
              <li key={index} className="bg-gray-50 border border-gray-300 p-3 rounded-lg text-sm">
                <div><strong>{tx.action}</strong> ${tx.amount} {tx.target && ` to/from: ${tx.target}`}</div>
                <div className="text-gray-500">{new Date(tx.timestamp).toLocaleString()}</div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  </div>
  );
}