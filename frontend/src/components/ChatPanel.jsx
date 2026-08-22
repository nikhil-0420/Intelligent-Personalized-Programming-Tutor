import { useState, useRef, useEffect } from "react";
import { ThumbsUp, ThumbsDown } from "lucide-react";
import MessageTrace from "./MessageTrace";
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

const MASTERY_THRESHOLD = 0.6;

function MasteryDelta({ before, after }) {
  if (before === undefined || before === null || after === undefined || after === null) return null;
  const delta = after - before;
  if (Math.abs(delta) < 0.001) return null;

  const crossedMastery = before < MASTERY_THRESHOLD && after >= MASTERY_THRESHOLD;
  const positive = delta > 0;

  return (
    <div
      className={`mt-2 inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 font-mono text-[10.5px] ${
        crossedMastery
          ? "animate-mastery-pulse border-pine/40 bg-pine/12 text-pine"
          : positive
          ? "border-pine/25 bg-pine/6 text-pine"
          : "border-clay/25 bg-clay/6 text-clay"
      }`}
      title={`p(know): ${before.toFixed(2)} -> ${after.toFixed(2)}`}
    >
      {positive ? "+" : ""}{(delta * 100).toFixed(0)}% mastery
      {crossedMastery && <span className="opacity-70"> · reached mastery</span>}
    </div>
  );
}

function CodeBlock({ language, codeString, ...props }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(codeString);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="relative my-1.5 group">
      <button
        onClick={handleCopy}
        className="absolute right-2 top-2 rounded-md border border-white/10 bg-black/40 px-2 py-1 font-mono text-[10px] text-white/70 opacity-0 transition-opacity group-hover:opacity-100 hover:text-white"
      >
        {copied ? "copied" : "copy"}
      </button>
      <SyntaxHighlighter style={oneDark} language={language} PreTag="div" {...props}>
        {codeString}
      </SyntaxHighlighter>
    </div>
  );
}

function FeedbackButtons({ interactionId, feedback, onFeedback }) {
  if (!interactionId || !onFeedback) return null;
  return (
    <div className="mt-2 flex items-center gap-1">
      <button
        onClick={() => onFeedback(interactionId, "up")}
        aria-label="Good response"
        className={`rounded-md p-1.5 transition-colors ${
          feedback === "up" ? "bg-pine/15 text-pine" : "text-muted hover:text-pine"
        }`}
      >
        <ThumbsUp size={14} strokeWidth={2} />
      </button>
      <button
        onClick={() => onFeedback(interactionId, "down")}
        aria-label="Poor response"
        className={`rounded-md p-1.5 transition-colors ${
          feedback === "down" ? "bg-clay/15 text-clay" : "text-muted hover:text-clay"
        }`}
      >
        <ThumbsDown size={14} strokeWidth={2} />
      </button>
    </div>
  );
}

export default function ChatPanel({ messages, onSend, loading, onAskQuestion, onFeedback }) {
  const [input, setInput] = useState("");
  const inputRef = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 160)}px`;
    }
  }, [input]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSend(input);
    setInput("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
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
            className={`animate-msg-in flex flex-col ${m.role === "student" ? "items-end" : "items-start"
              }`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 text-[14px] leading-relaxed ${m.role === "student"
                ? "bg-pine/8 text-text"
                : "font-voice border border-text/10 bg-base text-text"
                }`}
            >
              <div className="whitespace-pre-wrap">
                {m.role === "tutor" ? (
                  <ReactMarkdown
                    components={{
                      code({ inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || '');
                        const codeString = String(children).replace(/\n$/, '');
                        return !inline && match ? (
                          <CodeBlock language={match[1]} codeString={codeString} {...props} />
                        ) : (
                          <code className={className} {...props}>
                            {children}
                          </code>
                        );
                      },
                    }}
                  >
                    {m.text}
                  </ReactMarkdown>
                ) : (
                  m.text
                )}
              </div>
              {m.role === "tutor" && m.plannerNote && (
                <div className="font-voice-italic mt-2.5 border-t border-dashed border-clay/35 pt-2.5 text-[13px] text-clay">
                  <span className="opacity-60">— </span>
                  {m.plannerNote}
                </div>
              )}
              {m.role === "tutor" && m.isIntro && i === messages.length - 1 && (
                <div className="mt-3 flex gap-2 border-t border-text/10 pt-3">
                  <button
                    onClick={onAskQuestion}
                    className="rounded-lg border border-pine/30 bg-pine/8 px-3 py-1.5 text-xs font-medium text-pine hover:bg-pine/12"
                  >
                    Try a practice question
                  </button>
                  <button
                    onClick={() => inputRef.current?.focus()}
                    className="rounded-lg border border-text/15 px-3 py-1.5 text-xs text-muted hover:text-text"
                  >
                    Ask me anything
                  </button>
                </div>
              )}
              {m.role === "tutor" && m.isQuestion && (
                <div className="font-voice-italic mt-2.5 border-t border-dashed border-pine/35 pt-2.5 text-[13px] text-pine">
                  <span className="opacity-60">✎ </span>
                  practice question
                </div>
              )}
              {m.role === "tutor" && (
                <MasteryDelta before={m.pKnowBefore} after={m.pKnowAfter} />
              )}
            </div>
            {m.role === "tutor" && <MessageTrace trace={m.trace} />}
            {m.role === "tutor" && (
              <FeedbackButtons interactionId={m.interactionId} feedback={m.feedback} onFeedback={onFeedback} />
            )}
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="flex items-center gap-1.5 rounded-lg bg-base px-4 py-3">
              <span className="h-1.5 w-1.5 animate-shimmer-dot rounded-full bg-muted/50" style={{ animationDelay: "0ms" }} />
              <span className="h-1.5 w-1.5 animate-shimmer-dot rounded-full bg-muted/50" style={{ animationDelay: "150ms" }} />
              <span className="h-1.5 w-1.5 animate-shimmer-dot rounded-full bg-muted/50" style={{ animationDelay: "300ms" }} />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2.5 border-t border-text/10 p-3.5">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder="Ask a question or attempt an answer..."
          className="max-h-40 flex-1 resize-none rounded-lg border border-text/15 bg-base px-3.5 py-2.5 text-[13px] leading-normal text-text placeholder:text-muted focus:border-pine focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="self-end rounded-lg bg-pine px-5 py-2.5 text-[13px] font-medium text-base disabled:opacity-40"
        >
          Send
        </button>
      </form>
    </div>
  );
}