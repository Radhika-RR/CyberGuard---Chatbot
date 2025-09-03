// frontend/src/components/PhishChecker.jsx
import { useState } from "react";
import { checkPhish } from "../services/api";

export default function PhishChecker() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function onCheck() {
    setLoading(true);
    try {
      const r = await checkPhish(text);
      setResult(r);
    } catch (e) {
      setResult({ error: "Failed to contact backend." });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <h2>Phishing Checker</h2>
      <textarea
        rows={4}
        cols={80}
        placeholder="Paste URL or email text here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <div>
        <button onClick={onCheck} disabled={!text.trim() || loading}>
          {loading ? "Checking..." : "Check"}
        </button>
      </div>

      {result && (
        <div style={{ marginTop: 12, whiteSpace: "pre-wrap" }}>
          <strong>Prediction:</strong> {result.prediction}
          <br />
          <strong>Probability:</strong> {result.probability ?? "N/A"}
          <br />
          <strong>Features:</strong>
          <pre>{JSON.stringify(result.features, null, 2)}</pre>
          {result.error && <div style={{ color: "red" }}>{result.error}</div>}
        </div>
      )}
    </div>
  );
}
