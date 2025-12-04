// src/api.js
const BASE_URL = "http://localhost:8000"; // FastAPI backend

export async function analyzeIncident(text) {
  const res = await fetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  if (!res.ok) {
    throw new Error("Backend error");
  }

  return await res.json();
}
