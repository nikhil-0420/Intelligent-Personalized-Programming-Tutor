import { useState } from "react";
import MessageTrace from "./MessageTrace";

export default function ChatPanel({ messages, onSend, loading }) {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSend(input);
    setInput("");
  };

  return (
    <div className="flex h-full flex-col rounded-xl border border-text/10 bg-surface">
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="font-voice-italic pt-10 text-center text-sm text-muted">
            Ask a question, or try answering one — the tutor adapts to what you already know.
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`animate-msg-in flex flex-col ${
              m.role === "student" ? "items-end" : "items-start"
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 text-[14px] leading-relaxed ${
                m.role === "student"
                  ? "bg-pine/8 text-text"
                  : "font-voice border border-text/10 bg-base text-text"
              }`}
            >
              <div className="whitespace-pre-wrap">{m.text}</div>
              {m.role === "tutor" && m.plannerNote && (
                <div className="font-voice-italic mt-2.5 border-t border-dashed border-clay/35 pt-2.5 text-[13px] text-clay">
                  <span className="opacity-60">— </span>
                  {m.plannerNote}
                </div>
              )}
            </div>
            {m.role === "tutor" && <MessageTrace trace={m.trace} />}
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-lg bg-base px-4 py-2.5 text-sm text-muted">
              <span className="font-mono">thinking...</span>
            </div>
          </div>
        )}
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2.5 border-t border-text/10 p-3.5">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question or attempt an answer..."
          className="flex-1 rounded-lg border border-text/15 bg-base px-3.5 py-2.5 text-[13px] text-text placeholder:text-muted focus:border-pine focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-pine px-5 py-2.5 text-[13px] font-medium text-base disabled:opacity-40"
        >
          Send
        </button>
      </form>
    </div>
  );
}
