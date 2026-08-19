const NODES = [
  { key: "planner", label: "Planner", short: "PLN", tone: "pine" },
  { key: "assessor", label: "Assessor", short: "ASR", tone: "clay" },
  { key: "tutor", label: "Tutor", short: "TUT", tone: "pine" },
];

function readout(trace, key) {
  const frame = (trace || []).find((f) => f.agent === key);
  if (!frame) return null;
  if (key === "planner") return `routed to ${frame.recommended_topic}`;
  if (key === "assessor") return `is_attempt: ${frame.is_attempt}`;
  if (key === "tutor") return `grounding: ${frame.grounding_score?.toFixed(2)}`;
  return null;
}

export default function WaveformFlow({ trace }) {
  const hasTrace = !!trace && trace.length > 0;

  return (
    <div className="mb-5 rounded-xl border border-text/10 bg-surface px-6 pb-5 pt-7">
      <div className="mb-3 text-[11px] uppercase tracking-widest text-clay">
        {hasTrace ? "live agent flow" : "agent architecture"}
      </div>

      <svg width="100%" height="70" viewBox="0 0 620 70">
        <path d="M40,35 Q75,10 110,35 T180,35" fill="none" stroke="#2F5233" strokeWidth="1.5" opacity={hasTrace ? 1 : 0.35} />
        <path d="M180,35 Q230,60 280,35 T380,35" fill="none" stroke="#B5654A" strokeWidth="1.5" opacity={hasTrace ? 1 : 0.35} />
        <path d="M380,35 Q430,10 480,35 T580,35" fill="none" stroke="#2F5233" strokeWidth="1.5" opacity={hasTrace ? 1 : 0.35} />
        {hasTrace && (
          <circle cx="4" cy="35" r="4" fill="#2F5233">
            <animateMotion
              dur="3.2s"
              repeatCount="indefinite"
              path="M36,0 Q75,-25 110,0 T180,0 Q230,25 280,0 T380,0 Q430,-25 480,0 T580,0"
            />
          </circle>
        )}
      </svg>

      <div className="mt-1 flex justify-between">
        {NODES.map((node, i) => {
          const align = i === 0 ? "text-left" : i === 1 ? "text-center items-center" : "text-right justify-end";
          const borderColor = node.tone === "clay" ? "border-clay text-clay" : "border-pine text-pine";
          const text = readout(trace, node.key);
          return (
            <div key={node.key} className={`w-1/3 ${align}`}>
              <div className={`flex gap-2 ${i === 1 ? "justify-center" : i === 2 ? "justify-end" : ""} items-center`}>
                {i === 2 && (
                  <span className="font-voice-italic text-[13px] text-text">{node.label}</span>
                )}
                <div className={`flex h-[34px] w-[34px] items-center justify-center rounded-full border-2 font-mono text-[10px] font-medium ${borderColor}`}>
                  {node.short}
                </div>
                {i !== 2 && (
                  <span className="font-voice-italic text-[13px] text-text">{node.label}</span>
                )}
              </div>
              <div className="mt-1.5 font-mono text-[11px] text-muted">
                {text || "—"}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
