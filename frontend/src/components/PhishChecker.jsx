// frontend/src/components/PhishChecker.jsx
import React, { useState } from "react";
import API from "../services/api";

export default function PhishChecker() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await API.post("/api/phish/predict", { text });
      setResult(res.data);
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h3>Phish Checker</h3>
      <form onSubmit={submit}>
        <textarea value={text} onChange={e=>setText(e.target.value)} placeholder="paste URL, email or text here" rows={6} />
        <button type="submit">{loading ? "Checking..." : "Check"}</button>
      </form>
      {result && (
        <div>
          <h4>{result.label.toUpperCase()}</h4>
          <p>Probability: {(result.probability*100).toFixed(1)}%</p>
          <h5>Top features</h5>
          <ul>
            {result.features.map((f, idx) => (
              <li key={idx}>{f.feature} — contribution: {f.contribution.toFixed(4)}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
