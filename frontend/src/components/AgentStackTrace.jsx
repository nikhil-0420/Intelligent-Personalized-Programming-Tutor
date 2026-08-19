const AGENT_LABELS = { planner: "Planner", assessor: "Assessor", tutor: "Tutor" };

function StackFrame({ frame, depth }) {
  const label = AGENT_LABELS[frame.agent] || frame.agent;

  return (
    <div className="relative pl-6">
      {depth > 0 && <div className="absolute left-2 top-0 h-full w-px bg-text/10" />}
      <div className="absolute left-0 top-2 h-2 w-2 rounded-full bg-pine" />
      <div className="mb-3 rounded-lg border border-text/10 bg-base p-3">
        <div className="font-mono text-xs uppercase tracking-wider text-pine">{label}()</div>
        <div className="mt-1 space-y-0.5 font-mono text-xs text-muted">
          {frame.agent === "planner" && (
            <div>
              → recommended_topic: <span className="text-text">{frame.recommended_topic}</span>
            </div>
          )}
          {frame.agent === "assessor" && (
            <>
              <div>
                → is_attempt: <span className="text-text">{String(frame.is_attempt)}</span>
              </div>
              <div>
                → correct:{" "}
                <span className={frame.correct ? "text-pine" : "text-clay"}>{String(frame.correct)}</span>
              </div>
            </>
          )}
          {frame.agent === "tutor" && (
            <>
              <div>
                → retrieved_count: <span className="text-text">{frame.retrieved_count}</span>
              </div>
              <div>
                → grounding_score: <span className="text-text">{frame.grounding_score?.toFixed(3)}</span>
              </div>
            </>
          )}
        </div>
        {frame.reasoning && (
          <div className="font-voice-italic mt-2 border-t border-text/10 pt-2 text-xs text-muted">
            "{frame.reasoning}"
          </div>
        )}
      </div>
    </div>
  );
}

export default function AgentStackTrace({ trace, open, onToggle }) {
  if (!trace || trace.length === 0) return null;

  return (
    <div className="rounded-xl border border-text/10 bg-surface p-4">
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between font-mono text-[11px] uppercase tracking-widest text-muted"
      >
        <span>Full trace ({trace.length} frames)</span>
        <span className="text-pine">{open ? "hide" : "show"}</span>
      </button>
      {open && (
        <div className="mt-3">
          {trace.map((frame, i) => (
            <StackFrame key={i} frame={frame} depth={i} />
          ))}
        </div>
      )}
    </div>
  );
}
