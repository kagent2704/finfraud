import React from "react";

export default function Hero({ onGetStarted }: { onGetStarted: () => void }) {
  return (
    <section className="min-h-screen hero-bg flex items-center justify-center">
      <div className="text-center p-8">
        <h1 className="text-4xl font-bold mb-4">FinFraud — verifiable fraud detection</h1>
        <p className="mb-6 text-gray-300">Realtime detection, explainable consensus, and auditable ledger.</p>
        <button onClick={onGetStarted} className="px-6 py-3 rounded-lg bg-indigo-500 hover:bg-indigo-600">Get Started</button>
      </div>
    </section>
  );
}
