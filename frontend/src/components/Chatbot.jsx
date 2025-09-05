// frontend/src/components/Chatbot.jsx
import React, { useState } from "react";
import API from "../services/api";

export default function Chatbot() {
  const [question, setQuestion] = useState("");
  const [resp, setResp] = useState(null);
  const [loading, setLoading] = useState(false);

  const ask = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const r = await API.post("/api/chat_web", { question });
      setResp(r.data);
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h3>Cybersecurity Chatbot</h3>
      <form onSubmit={ask}>
        <input value={question} onChange={e=>setQuestion(e.target.value)} placeholder="How to detect phishing emails?" />
        <button type="submit">{loading ? "Searching..." : "Ask"}</button>
      </form>

      {resp && (
        <div>
          <h4>Answer</h4>
          <p>{resp.summary}</p>
          <h5>Sources</h5>
          <ul>
            {resp.sources.map((s, i) => (
              <li key={i}><a href={s.link} target="_blank" rel="noreferrer">{s.title || s.link}</a></li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
