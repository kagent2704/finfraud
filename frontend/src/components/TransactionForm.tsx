import { useState } from "react";
import { apiFetch } from "../api/client";

export default function TransactionForm({ onComplete }: { onComplete: (txnId: string) => void }) {
  const [amount, setAmount] = useState("");
  const [sender, setSender] = useState("");
  const [receiver, setReceiver] = useState("");
  const [location, setLocation] = useState("Pune");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await apiFetch("/api/predict", {
        method: "POST",
        body: JSON.stringify({
          external_txn_id: crypto.randomUUID(),
          user_external_id: sender,
          amount: parseFloat(amount),
          currency: "INR",
          merchant_id: receiver,
          device_id: "web-client",
          location, // ✅ send dropdown value
          device_risk_score: 0.1,
        }),
      });
      console.log("✅ Transaction created:", res);
      onComplete(res.transaction_id); // backend returns transaction_id
    } catch (err: any) {
      setError(err.message || "Failed to create transaction");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-6 bg-gray-900/60 rounded-lg">
      <input
        type="number"
        placeholder="Amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        className="w-full px-4 py-2 bg-gray-800 rounded-lg"
      />
      <input
        type="text"
        placeholder="Sender (user_external_id)"
        value={sender}
        onChange={(e) => setSender(e.target.value)}
        className="w-full px-4 py-2 bg-gray-800 rounded-lg"
      />
      <input
        type="text"
        placeholder="Receiver (merchant_id)"
        value={receiver}
        onChange={(e) => setReceiver(e.target.value)}
        className="w-full px-4 py-2 bg-gray-800 rounded-lg"
      />

      {/* ✅ Location Dropdown */}
      <select
        value={location}
        onChange={(e) => setLocation(e.target.value)}
        className="w-full px-4 py-2 bg-gray-800 rounded-lg"
      >
        <option value="Bangalore">Bangalore</option>
        <option value="Delhi">Delhi</option>
        <option value="EU">EU</option>
        <option value="Mumbai">Mumbai</option>
        <option value="Pune">Pune</option>
        <option value="Russia">Russia</option>
        <option value="mobile">mobile</option>
        <option value="other">other</option>
      </select>

      <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-semibold">
        Submit Transaction
      </button>
      {error && <p className="text-red-500">{error}</p>}
    </form>
  );
}
