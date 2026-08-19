const NODES = [
  { key: "planner", label: "Planner", short: "PLN", tone: "gold" },
  { key: "assessor", label: "Assessor", short: "ASR", tone: "rose" },
  { key: "tutor", label: "Tutor", short: "TUT", tone: "gold" },
];

function Node({ node, active }) {
  const toneClasses =
    node.tone === "rose"
      ? "border-rose text-rose bg-rose/10 shadow-[0_0_16px_rgba(184,103,122,0.3)]"
      : "border-gold text-gold bg-gold/10 shadow-[0_0_16px_rgba(201,154,61,0.3)]";

  return (
    <div className="flex flex-col items-center gap-2">
      <div
        className={`flex h-11 w-11 items-center justify-center rounded-full border-2 font-mono text-[10px] font-bold transition-opacity duration-300 ${toneClasses} ${
          active ? "opacity-100" : "opacity-40"
        }`}
      >
        {node.short}
      </div>
      <div className="font-voice-italic text-xs text-muted">{node.label}</div>
    </div>
  );
}

function Connector({ delay, active }) {
  return (
    <div className="relative mx-1.5 -mt-[22px] h-0.5 flex-1 bg-gradient-to-r from-gold to-muted/10">
      {active && (
        <div
          className="absolute top-1/2 h-1.5 w-1.5 -translate-y-1/2 rounded-full bg-gold shadow-[0_0_10px_#C99A3D]"
          style={{
            animation: "flow-travel 2.6s linear infinite",
            animationDelay: `${delay}s`,
          }}
        />
      )}
      <style>{`
        @keyframes flow-travel {
          0% { left: 0%; opacity: 1; }
          90% { opacity: 1; }
          100% { left: 96%; opacity: 0; }
        }
      `}</style>
    </div>
  );
}

export default function AgentFlowDiagram({ trace }) {
  const firedAgents = new Set((trace || []).map((f) => f.agent));
  const hasTrace = firedAgents.size > 0;

  return (
    <div className="mb-5 rounded-xl border border-muted/15 bg-surface p-5">
      <div className="mb-1 font-mono text-[11px] uppercase tracking-widest text-gold">
        {hasTrace ? "Live agent flow" : "Agent architecture"}
      </div>
      <div className="flex items-center justify-between px-1.5 pb-1.5 pt-5">
        {NODES.map((node, i) => (
          <div key={node.key} className="flex flex-1 items-center last:flex-none">
            <Node node={node} active={!hasTrace || firedAgents.has(node.key)} />
            {i < NODES.length - 1 && (
              <Connector delay={i * 0.85} active={hasTrace} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
