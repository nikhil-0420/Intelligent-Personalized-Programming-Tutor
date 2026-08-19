export default function TopicChip({ topicSlug, pKnow, onChange }) {
  const pct = Math.round((pKnow ?? 0) * 100);

  return (
    <button
      onClick={onChange}
      className="flex items-center gap-2 rounded-full border border-pine/30 bg-surface py-1 pl-1.5 pr-3 transition-colors hover:border-pine/50"
    >
      <div className="flex h-[22px] w-[22px] items-center justify-center rounded-full bg-pine/10 font-mono text-[10px] text-pine">
        {topicSlug?.[0]?.toUpperCase()}
      </div>
      <span className="font-voice-italic text-[13px] text-text">{topicSlug?.replace(/_/g, " ")}</span>
      <span className="font-mono text-[10px] text-muted">{pct}%</span>
    </button>
  );
}
