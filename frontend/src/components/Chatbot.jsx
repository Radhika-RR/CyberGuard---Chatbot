// frontend/src/components/Chatbot.jsx
import { useState } from "react";
import { askChatWeb } from "../services/api";

export default function Chatbot() {
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function onAsk() {
    setLoading(true);
    setError(null);
    try {
      const r = await askChatWeb(q);
      setAnswer(r);
    } catch (e) {
      setError("Failed to fetch answer. Check backend and SERPAPI key.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <h2>Cyber Awareness Chat (Web Enabled)</h2>
      <div>
        <input
          type="text"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          style={{ width: "70%" }}
          placeholder="Ask anything about cybersecurity..."
        />
        <button onClick={onAsk} disabled={loading || !q.trim()}>
          {loading ? "Searching..." : "Ask"}
        </button>
      </div>

      {error && <div style={{ color: "red", marginTop: 8 }}>{error}</div>}

      {answer && (
        <div style={{ marginTop: 16 }}>
          <h4>Summary</h4>
          <p>{answer.summary || "No summary available."}</p>

          <h4>Sources</h4>
          <ul>
            {Array.isArray(answer.sources) && answer.sources.length > 0 ? (
              answer.sources.map((s, i) => (
                <li key={i} style={{ marginBottom: 8 }}>
                  <a href={s.link} target="_blank" rel="noreferrer">
                    {s.title || s.link}
                  </a>
                  <div style={{ fontSize: 13 }}>{s.snippet}</div>
                </li>
              ))
            ) : (
              <li>No sources found.</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
