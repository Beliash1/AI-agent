import { useState, useRef, useEffect } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/agent";

function generateSessionId() {
  return "cici-" + Math.random().toString(36).slice(2, 10);
}

const ACTION_LABELS = {
  delegate_researcher: "ვებ კვლევა",
  delegate_coder: "კოდის აგენტი",
  fetch_url: "გვერდის წაკითხვა",
  make_plan: "დაგეგმვა",
  final_answer: "პასუხი",
};

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [model, setModel] = useState("qwen3:4b");
  const [status, setStatus] = useState("idle");
  const [trace, setTrace] = useState([]);
  const [online, setOnline] = useState(null);
  const sessionId = useRef(generateSessionId());
  const scrollRef = useRef(null);

  useEffect(() => {
    fetch(API_URL.replace("/agent", "/docs"))
      .then(() => setOnline(true))
      .catch(() => setOnline(false));
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  async function sendMessage() {
    const text = input.trim();
    if (!text || status === "thinking") return;

    setMessages((m) => [...m, { role: "user", text }]);
    setInput("");
    setStatus("thinking");
    setTrace([]);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          model,
          session_id: sessionId.current,
        }),
      });

      if (!res.ok) throw new Error(`სერვერმა დააბრუნა ${res.status}`);

      const data = await res.json();
      setTrace(data.steps || []);

      const raw =
        data.answer ??
        data.response ??
        data.output ??
        data.message?.content ??
        data.content ??
        data;

      const botReply =
        typeof raw === "string"
          ? raw
          : JSON.stringify(raw, null, 2);

      setMessages((m) => [...m, { role: "assistant", text: botReply }]);
      setStatus("idle");
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: "error",
          text: `კავშირის შეცდომა: ${err.message}`,
        },
      ]);
      setStatus("error");
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-ring" data-active={status === "thinking"} />
          <span className="brand-name">CICI</span>
        </div>

        <select
          className="model-select"
          value={model}
          onChange={(e) => setModel(e.target.value)}
        >
          <option value="qwen3:4b">qwen3:4b</option>
          <option value="qwen3:8b">qwen3:8b</option>
        </select>

        <div className="status-pill" data-state={online ? "on" : "off"}>
          <span className="dot" />
          {online === null ? "მოწმდება..." : online ? "ონლაინ" : "ხაზგარეშე"}
        </div>
      </header>

      <main className="board">
        <section className="core-panel">
          <div className="core-ring" data-thinking={status === "thinking"}>
            <div className="core-ring__arc arc-1" />
            <div className="core-ring__arc arc-2" />
            <div className="core-ring__arc arc-3" />
            <div className="core-ring__center">
              {status === "thinking"
                ? "ANALYZING"
                : status === "error"
                ? "ERROR"
                : "READY"}
            </div>
          </div>

          <div className="conversation" ref={scrollRef}>
            {messages.length === 0 && (
              <p className="empty-hint">
                დაწერე მოთხოვნა — Cici გამოიძახებს საჭირო ქვე-აგენტს.
              </p>
            )}

            {messages.map((m, i) => (
              <div key={i} className={`bubble bubble--${m.role}`}>
                <span className="bubble__label">
                  {m.role === "user"
                    ? "შენ"
                    : m.role === "error"
                    ? "სისტემა"
                    : "CICI"}
                </span>
                <pre style={{ whiteSpace: "pre-wrap" }}>
                  {String(m.text)}
                </pre>
              </div>
            ))}
          </div>
        </section>

        <aside className="trace-panel">
          <h2>AGENT TRACE</h2>
          {trace.length === 0 ? (
            <p className="trace-empty">
              აქ გამოჩნდება აგენტის ნაბიჯები რეალურ დროში.
            </p>
          ) : (
            <ol className="trace-list">
              {trace.map((step, i) => (
                <li key={i} className="trace-item">
                  <span className="trace-index">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <div>
                    <div className="trace-action">
                      {ACTION_LABELS[step.action] || step.action}
                    </div>
                    <div className="trace-output">
                      {typeof step.output === "string"
                        ? step.output.slice(0, 140)
                        : JSON.stringify(step.output, null, 2).slice(0, 140)}
                      {(JSON.stringify(step.output)?.length || 0) > 140 && "…"}
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          )}
        </aside>
      </main>

      <footer className="composer">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="მიწერე Cici-ს..."
          rows={1}
        />
        <button onClick={sendMessage} disabled={status === "thinking"}>
          {status === "thinking" ? "..." : "გაგზავნა"}
        </button>
      </footer>
    </div>
  );
}
