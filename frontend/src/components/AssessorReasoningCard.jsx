export default function AssessorReasoningCard({ trace }) {
  const frame = (trace || []).find((f) => f.agent === "assessor");

  return (
    <div className="rounded-xl border border-text/10 bg-surface p-4">
      <div className="mb-3 text-[11px] uppercase tracking-widest text-muted">Assessor reasoning</div>
      {frame ? (
        <>
          {frame.reasoning && (
            <div className="font-voice-italic border-t border-dashed border-clay/35 pt-2.5 text-[13px] leading-relaxed text-clay">
              <span className="opacity-60">— </span>"{frame.reasoning}"
            </div>
          )}
          <div className="mt-3.5 flex gap-4 font-mono text-[11px] text-muted">
            <span>
              is_attempt: <span className="text-text">{String(frame.is_attempt)}</span>
            </span>
            <span>
              correct:{" "}
              <span className={frame.correct ? "text-pine" : "text-clay"}>{String(frame.correct)}</span>
            </span>
          </div>
        </>
      ) : (
        <div className="text-xs text-muted">No judgment yet — send a message to see it here.</div>
      )}
    </div>
  );
}
