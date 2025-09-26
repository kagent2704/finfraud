// frontend/src/pages/Dashboard.tsx
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { Shield, Database, BarChart3, Blocks } from "lucide-react";
import { useState } from "react";
import { apiFetch } from "../api/client";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [fraudResult, setFraudResult] = useState<any | null>(null);
  const [recommendations, setRecommendations] = useState<any | null>(null);
  const [transaction, setTransaction] = useState<any | null>(null);
  const [chain, setChain] = useState<any | null>(null);
  const [lastTxnId, setLastTxnId] = useState<number | null>(null);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  // --- Button Handlers ---
  const runFraudCheck = async () => {
    try {
      const result = await apiFetch("/api/predict", {
        method: "POST",
        body: JSON.stringify({
          external_txn_id: crypto.randomUUID(),
          user_external_id: "AMZ",
          amount: 20000 + Math.floor(Math.random() * 100000),
          currency: "INR",
          merchant_id: "TestMerchant",
          device_id: "web-client",
          location: "Pune",
          device_risk_score: Math.random(),
        }),
      });
      console.log("Fraud Check:", result);
      setFraudResult(result);
      setLastTxnId(result.transaction_id);
    } catch (err: any) {
      alert("Fraud check failed: " + err.message);
    }
  };

  const getRecommendations = async () => {
    if (!lastTxnId) return alert("Run a transaction first!");
    try {
      const recs = await apiFetch(`/api/recommendations/${lastTxnId}`);
      console.log("Recommendations:", recs);
      setRecommendations(recs);
    } catch (err: any) {
      alert("Failed to fetch recommendations: " + err.message);
    }
  };

  const viewTransactions = async () => {
    if (!lastTxnId) return alert("Run a transaction first!");
    try {
      const txn = await apiFetch(`/api/transactions/${lastTxnId}`);
      console.log("Transaction:", txn);
      setTransaction(txn);
    } catch (err: any) {
      alert("Failed to fetch transaction: " + err.message);
    }
  };

  const viewChain = async () => {
    try {
      const latest = await apiFetch(`/chain/latest`);
      console.log("Latest Block:", latest);
      setChain(latest);
    } catch (err: any) {
      alert("Failed to fetch chain: " + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-800 text-white">
      {/* Navbar */}
      <nav className="flex items-center justify-between px-8 py-4 bg-gray-900/60 backdrop-blur-md shadow-md">
        <div className="flex items-center space-x-3">
          <img src="/LOGO.png" alt="FinFraud Logo" className="h-8 w-8" />
          <h1 className="text-2xl font-bold">FinFraud Dashboard</h1>
        </div>
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-500 hover:bg-red-600 rounded-lg font-semibold"
        >
          Logout
        </button>
      </nav>

      {/* Welcome Section */}
      <div className="text-center mt-12">
        <h2 className="text-3xl font-extrabold">Welcome, {user?.email} 👋</h2>
        <p className="text-gray-400 mt-2">
          Manage fraud detection, transactions, and insights
        </p>
      </div>

      {/* Results Cards */}
      <div className="mt-8 px-12 grid gap-6">
        {fraudResult && (
          <div className="p-6 bg-gray-900/60 rounded-xl border border-gray-700">
            <h3 className="text-xl font-bold mb-2">Fraud Detection Result</h3>
            <p>
              <strong>Transaction ID:</strong> {fraudResult.transaction_id}
            </p>
            <p>
              <strong>Verdict:</strong>{" "}
              <span
                className={
                  fraudResult.verdict === "fraud" ? "text-red-400" : "text-green-400"
                }
              >
                {fraudResult.verdict.toUpperCase()}
              </span>
            </p>
            <p>
              <strong>Fraud Score:</strong> {fraudResult.fraud_score.toFixed(2)}
            </p>
            <p>
              <strong>Consensus Score:</strong>{" "}
              {fraudResult.consensus_score.toFixed(2)}
            </p>
            <p>
              <strong>Confidence:</strong>{" "}
              {fraudResult.recs?.confidence?.toFixed(2) || "N/A"}
            </p>
          </div>
        )}

        {recommendations && (
          <div className="p-6 bg-gray-900/60 rounded-xl border border-gray-700">
            <h3 className="text-xl font-bold mb-2">Recommendations</h3>
            <pre className="text-sm text-gray-300">
              {JSON.stringify(recommendations.recommendations, null, 2)}
            </pre>
            <p className="mt-2 text-gray-400">
              Confidence: {recommendations.confidence?.toFixed(2)}
            </p>
          </div>
        )}

        {transaction && (
          <div className="p-6 bg-gray-900/60 rounded-xl border border-gray-700">
            <h3 className="text-xl font-bold mb-2">Transaction Details</h3>
            <pre className="text-sm text-gray-300">
              {JSON.stringify(transaction, null, 2)}
            </pre>
          </div>
        )}

        {chain && (
          <div className="p-6 bg-gray-900/60 rounded-xl border border-gray-700">
            <h3 className="text-xl font-bold mb-2">Latest Chain Block</h3>
            <pre className="text-sm text-gray-300">
              {JSON.stringify(chain, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {/* Features Grid */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 px-12">
        <div className="p-6 bg-gray-900/60 backdrop-blur-xl rounded-xl shadow-lg border border-gray-700 hover:scale-105 transition">
          <Shield className="h-6 w-6 mb-3 text-indigo-400" />
          <h3 className="text-xl font-semibold mb-2">Fraud Detection</h3>
          <p className="text-gray-400 mb-4">Run fraud checks in real time.</p>
          <button
            onClick={runFraudCheck}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-semibold"
          >
            Run Check
          </button>
        </div>

        <div className="p-6 bg-gray-900/60 backdrop-blur-xl rounded-xl shadow-lg border border-gray-700 hover:scale-105 transition">
          <Database className="h-6 w-6 mb-3 text-indigo-400" />
          <h3 className="text-xl font-semibold mb-2">Transactions</h3>
          <p className="text-gray-400 mb-4">View & analyze your transactions.</p>
          <button
            onClick={viewTransactions}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-semibold"
          >
            View Transactions
          </button>
        </div>

        <div className="p-6 bg-gray-900/60 backdrop-blur-xl rounded-xl shadow-lg border border-gray-700 hover:scale-105 transition">
          <BarChart3 className="h-6 w-6 mb-3 text-indigo-400" />
          <h3 className="text-xl font-semibold mb-2">Recommendations</h3>
          <p className="text-gray-400 mb-4">AI-powered fraud prevention tips.</p>
          <button
            onClick={getRecommendations}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-semibold"
          >
            Get Insights
          </button>
        </div>

        <div className="p-6 bg-gray-900/60 backdrop-blur-xl rounded-xl shadow-lg border border-gray-700 hover:scale-105 transition">
          <Blocks className="h-6 w-6 mb-3 text-indigo-400" />
          <h3 className="text-xl font-semibold mb-2">Audit Chain</h3>
          <p className="text-gray-400 mb-4">Explore blockchain ledger entries.</p>
          <button
            onClick={viewChain}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-semibold"
          >
            View Chain
          </button>
        </div>
      </div>
    </div>
  );
}
