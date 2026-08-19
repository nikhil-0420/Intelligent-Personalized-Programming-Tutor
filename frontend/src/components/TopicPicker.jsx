const CIRC = 2 * Math.PI * 16;

function MasteryRing({ pct, tone }) {
  const offset = CIRC - (pct / 100) * CIRC;
  const color = tone === "clay" ? "#B5654A" : "#2F5233";
  return (
    <svg width="40" height="40" viewBox="0 0 40 40" className="mx-auto mb-1">
      <circle cx="20" cy="20" r="16" fill="none" stroke="rgba(47,82,51,0.15)" strokeWidth="3" />
      <circle
        cx="20"
        cy="20"
        r="16"
        fill="none"
        stroke={color}
        strokeWidth="3"
        strokeDasharray={CIRC}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform="rotate(-90 20 20)"
        style={{ transition: "stroke-dashoffset 0.6s ease-out" }}
      />
    </svg>
  );
}

export default function TopicPicker({ topics, skills, recommendation, onSelect }) {
  const skillMap = Object.fromEntries((skills || []).map((s) => [s.topic_slug, s.p_know]));
  const blockedSet = new Set((recommendation?.blocked_topics || []).map((b) => b.topic));
  const suggested = recommendation?.recommended_topic;

  return (
    <div className="rounded-xl border border-text/10 bg-surface p-6">
      <div className="mb-5 text-center">
        <div className="font-voice-italic mb-1 text-[13px] text-clay">what should we work on?</div>
        <div className="font-display text-xl font-bold text-text">Choose a topic to begin</div>
      </div>

      <div className="grid grid-cols-4 gap-2.5">
        {topics.map((t) => {
          const pKnow = skillMap[t.slug] ?? 0.1;
          const pct = Math.round(pKnow * 100);
          const isLocked = blockedSet.has(t.slug);
          const isSuggested = t.slug === suggested;

          return (
            <button
              key={t.slug}
              disabled={isLocked}
              onClick={() => onSelect(t.slug)}
              className={`relative rounded-lg p-3 text-center transition-all ${
                isLocked
                  ? "cursor-not-allowed border border-dashed border-text/15 opacity-50"
                  : isSuggested
                  ? "border-[1.5px] border-pine bg-white hover:shadow-sm"
                  : "border border-text/10 bg-white hover:border-pine/40 hover:shadow-sm"
              }`}
            >
              {isSuggested && (
                <div className="absolute right-1.5 top-1.5 rounded-full bg-clay/10 px-1.5 py-0.5 font-mono text-[8px] text-clay">
                  suggested
                </div>
              )}
              {isLocked ? (
                <svg width="40" height="40" viewBox="0 0 40 40" className="mx-auto mb-1">
                  <circle cx="20" cy="20" r="16" fill="none" stroke="rgba(33,29,24,0.12)" strokeWidth="3" />
                </svg>
              ) : (
                <MasteryRing pct={pct} tone={isSuggested ? "clay" : "pine"} />
              )}
              <div className="font-voice-italic text-xs text-text">
                {t.title || t.slug.replace(/_/g, " ")}
              </div>
              <div className="font-mono text-[10px] text-muted">{isLocked ? "locked" : `${pct}%`}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
