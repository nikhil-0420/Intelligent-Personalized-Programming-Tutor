export default function TopicChip({ topicSlug, pKnow, onChange }) {
  const pct = Math.round((pKnow ?? 0) * 100);

  const radius = 9;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (pct / 100) * circumference;

  return (
    <button
      onClick={onChange}
      className="flex items-center gap-2 rounded-full border border-pine/30 bg-surface py-1 pl-1.5 pr-3 transition-colors hover:border-pine/50"
    >
      <div className="relative flex h-[22px] w-[22px] items-center justify-center">
        <svg width="22" height="22" viewBox="0 0 22 22" className="-rotate-90">
          <circle cx="11" cy="11" r={radius} fill="none" stroke="currentColor" strokeWidth="2" className="text-pine/12" />
          <circle
            cx="11" cy="11" r={radius} fill="none" stroke="currentColor" strokeWidth="2"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="text-pine transition-[stroke-dashoffset] duration-500"
          />
        </svg>
        <span className="absolute font-mono text-[8px] text-pine">
          {topicSlug?.[0]?.toUpperCase()}
        </span>
      </div>
      <span className="font-voice-italic text-[13px] text-text">{topicSlug?.replace(/_/g, " ")}</span>
      <span className="font-mono text-[10px] text-muted">{pct}%</span>
    </button>
  );
}