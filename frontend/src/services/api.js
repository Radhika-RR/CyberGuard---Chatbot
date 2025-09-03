// frontend/src/services/api.js
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function checkPhish(text) {
  const res = await fetch(`${API_BASE}/api/phish/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return res.json();
}

export async function askChatWeb(question) {
  const res = await fetch(`${API_BASE}/api/chat_web`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return res.json();
}

export async function askChatKB(question) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return res.json();
}
