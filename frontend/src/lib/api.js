/**
 * lib/api.js — Cici backend-თან HTTP კომუნიკაციის ერთადერთი ადგილი.
 *
 * ადრე ეს ფაილი საერთოდ არ გამოიყენებოდა — App.jsx-ს თავისი, დუბლირებული
 * fetch-ლოგიკა ჰქონდა ჩაშენებული. ახლა ორივე ერთ წყაროზეა დაყვანილი.
 */

const API_BASE = "http://127.0.0.1:8000";

/**
 * უგზავნის მომხმარებლის შეტყობინებას /agent endpoint-ს.
 * აბრუნებს: { answer, response, steps: [{action, input, output}, ...] }
 */
export async function askAgent(message, { model = "qwen3:4b", sessionId = "default" } = {}) {
  const res = await fetch(`${API_BASE}/agent`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, model, session_id: sessionId }),
  });

  if (!res.ok) {
    throw new Error(`სერვერმა დააბრუნა ${res.status}`);
  }

  return await res.json();
}

/** გაასუფთავებს კონკრეტული სესიის მეხსიერებას ("ახალი საუბრის" ღილაკისთვის). */
export async function clearSession(sessionId) {
  const res = await fetch(`${API_BASE}/agent/session/${sessionId}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    throw new Error(`სესიის გასუფთავება ვერ მოხერხდა (${res.status})`);
  }

  return await res.json();
}

/** ამოწმებს არის თუ არა backend ხელმისაწვდომი (status pill-ისთვის). */
export async function checkOnline() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
