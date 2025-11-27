import React, { useState } from "react";
import "./App.css";

function App() {
  const [showPopup, setShowPopup] = useState(false);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("Idle");
  const [result, setResult] = useState(null); // { label, score, flags, error }

  const openPopup = () => setShowPopup(true);
  const closePopup = () => {
    setShowPopup(false);
    setStatus("Idle");
  };

  const handleAnalyze = async () => {
    const trimmed = text.trim();
    if (!trimmed) {
      alert("Paste some text first.");
      return;
    }

    setLoading(true);
    setStatus("Analyzing…");
    setResult(null);

    try {
      // Call our Flask API endpoint `/api/classify-all` which returns
      // structured JSON (overall, tweet, profile, urls, image)
      const res = await fetch("/api/classify-all", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tweet_text: trimmed, profile: null, urls: [], image_base64: null }),
      });

      if (!res.ok) throw new Error("Backend error: " + res.status);

      const data = await res.json();

      // Map backend response to the UI's expected shape
      const overall = data.overall || {};
      const tweet = data.tweet || {};
      const profile = data.profile || {};

      const label = (overall.classification || tweet.classification || profile.classification || "UNKNOWN").toUpperCase();
      // backend uses percentages 0-100 for probabilities; UI expects 0-1 number for score in some places
      const scoreRaw = tweet.probability ?? overall.confidence ?? profile.probability ?? null;
      const score = typeof scoreRaw === "number" ? (scoreRaw / 100) : null;
      // Collect flags if present
      const flags = (data.flags || [])
        .concat(tweet.flags || [])
        .concat(profile.flags || [])
        .slice(0, 10);

      setResult({ label, score, flags, error: null });
      setStatus("Done");
    } catch (err) {
      console.error(err);
      setResult({
        label: "UNKNOWN",
        score: null,
        flags: [],
        error: "Backend not reachable.",
      });
      setStatus("Error");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setText("");
    setResult(null);
    setStatus("Idle");
  };

  const getScorePercent = () => {
    if (!result || typeof result.score !== "number") return null;
    return Math.round(result.score * 100);
  };

  const getRiskClass = () => {
    const pct = getScorePercent();
    if (pct == null) return "";
    if (pct < 40) return "score-safe";
    if (pct < 70) return "score-medium";
    return "score-high";
  };

  const getSummary = () => {
    if (!result) return "";
    const { label } = result;
    if (label === "FAKE") return "Looks FAKE / high risk.";
    if (label === "REAL") return "Looks REAL / low risk.";
    return "Not sure. Be careful.";
  };

  return (
    <div className="app-root">
      <div className="app-shell">
        {/* Tiny header */}
        <header className="app-header">
          <div className="logo">
            <div className="logo-icon">
              <svg viewBox="0 0 24 24" fill="none">
                <path
                  d="M12 2.5L5 5.5V11.5C5 16.3 8 19.9 12 21.5C16 19.9 19 16.3 19 11.5V5.5L12 2.5Z"
                  stroke="white"
                  strokeWidth="1.4"
                  strokeLinejoin="round"
                />
                <path
                  d="M10 10.7L11.4 12.1L14.4 9.1"
                  stroke="white"
                  strokeWidth="1.4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
            <div>
              <h1>Fake News Checker</h1>
              <p>Check if text is fake or real.</p>
            </div>
          </div>
        </header>

        {/* Just one button on the page */}
        <main className="app-main">
          <button className="btn-primary main-btn" onClick={openPopup}>
            🔍 Open Checker
          </button>
        </main>
      </div>

      {/* Floating icon bottom-right */}
      <button
        className="fab-button"
        onClick={openPopup}
        aria-label="Open fake news analyzer"
      >
        <svg className="fab-icon" viewBox="0 0 24 24" fill="none">
          <path
            d="M12 2.5L5 5.5V11.5C5 16.3 8 19.9 12 21.5C16 19.9 19 16.3 19 11.5V5.5L12 2.5Z"
            stroke="white"
            strokeWidth="1.6"
            strokeLinejoin="round"
          />
          <path
            d="M10 10.7L11.4 12.1L14.4 9.1"
            stroke="white"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {/* Popup */}
      <div
        className={`popup-overlay ${showPopup ? "visible" : ""}`}
        onClick={closePopup}
      >
        <div
          className="popup-card"
          onClick={(e) => e.stopPropagation()}
        >
          <button className="popup-close" onClick={closePopup}>
            ×
          </button>

          <div className="popup-header">
            <h2>Check text</h2>
            <p>Paste and analyze.</p>
          </div>

          <textarea
            className="checker-input"
            placeholder="Paste news/post text here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />

          <div className="checker-actions">
            <button
              className="btn-primary"
              onClick={handleAnalyze}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner" /> Analyzing...
                </>
              ) : (
                <>🔍 Analyze</>
              )}
            </button>
            <button
              className="btn-secondary"
              type="button"
              onClick={handleClear}
            >
              Clear
            </button>
            <span className="status-text">Status: {status}</span>
          </div>

          {result && (
            <div className="result-card">
              <div className="result-row">
                <span className="result-label">
                  Result:{" "}
                  <span
                    className={`label-chip label-${result.label.toLowerCase()}`}
                  >
                    {result.label}
                  </span>
                </span>
                <span className={`score-text ${getRiskClass()}`}>
                  {getScorePercent() != null
                    ? `${getScorePercent()}% fake`
                    : "--"}
                </span>
              </div>

              <div className="meter">
                <div className="meter-track">
                  <div
                    className="meter-fill"
                    style={{
                      width:
                        getScorePercent() != null
                          ? `${getScorePercent()}%`
                          : "0%",
                    }}
                  />
                </div>
                <div className="meter-scale">
                  <span>Real</span>
                  <span>Fake</span>
                </div>
              </div>

              <p className="summary-text">{getSummary()}</p>

              {result.error && (
                <p className="error-text">{result.error}</p>
              )}

              <div className="flags">
                {(result.flags || []).length > 0 ? (
                  result.flags.map((f, i) => (
                    <span key={i} className="flag-chip">
                      {f}
                    </span>
                  ))
                ) : (
                  <span className="flag-chip">
                    No extra details.
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;