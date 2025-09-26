import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
export default function Home() {
  const { login, signup } = useAuth();
  const [showModal, setShowModal] = useState(false);
  const [mode, setMode] = useState<"signin" | "signup">("signin");

  // form state
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();
  // handle form submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      if (mode === "signin") {
        // ✅ delegate to AuthContext login
        await login(email, password);
      } else {
        // ✅ delegate to AuthContext signup
        await signup(name, email, password);
      }

      setShowModal(false); // close modal after success
      navigate("/dashboard"); // ✅ auto-redirect after auth
    } catch (err) {
      setError("Failed to fetch");
    }
  };

  return (
    <div className="relative flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-800 overflow-hidden text-white">
      
      {/* Rotating background image */}
      <div className="absolute inset-0 flex items-center justify-center">
        <img
          src="/LOGO.png" // make sure logo.png is inside frontend/public/
          alt="Rotating Logo"
          className="w-2/3 opacity-10 animate-spin-slow"
        />
      </div>

      {/* Hero Section */}
      <div className="relative z-10 text-center">
        <h1 className="text-5xl font-extrabold mb-4">
          FinFraud — verifiable fraud detection
        </h1>
        <p className="text-gray-400 mb-8">
          Realtime detection, explainable consensus, and auditable ledger.
        </p>
        <button
          onClick={() => setShowModal(true)}
          className="px-8 py-3 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-semibold shadow-lg"
        >
          Get Started
        </button>
      </div>

      {/* Sign In / Sign Up Modal */}
      {showModal && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm z-20">
          <div className="bg-gray-900/60 backdrop-blur-xl rounded-xl shadow-xl p-8 w-96 border border-gray-700">
            <h2 className="text-2xl font-bold mb-6 text-center">
              {mode === "signin" ? "Sign In" : "Sign Up"}
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              {mode === "signup" && (
                <input
                  type="text"
                  placeholder="Full Name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-2 bg-gray-800/70 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              )}

              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 bg-gray-800/70 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 bg-gray-800/70 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />

              {error && <p className="text-red-400 text-sm">{error}</p>}

              <button
                type="submit"
                className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-semibold"
              >
                {mode === "signin" ? "Sign In" : "Create Account"}
              </button>
            </form>

            <p className="mt-4 text-sm text-gray-400 text-center">
              {mode === "signin" ? (
                <>
                  Don’t have an account?{" "}
                  <button
                    onClick={() => setMode("signup")}
                    className="text-indigo-400 hover:underline"
                  >
                    Sign Up
                  </button>
                </>
              ) : (
                <>
                  Already have an account?{" "}
                  <button
                    onClick={() => setMode("signin")}
                    className="text-indigo-400 hover:underline"
                  >
                    Sign In
                  </button>
                </>
              )}
            </p>

            <button
              onClick={() => setShowModal(false)}
              className="mt-4 text-gray-400 hover:text-white w-full"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
