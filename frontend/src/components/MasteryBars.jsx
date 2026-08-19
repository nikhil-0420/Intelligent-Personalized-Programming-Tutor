export default function MasteryBars({ skills }) {
  const sorted = [...skills].sort((a, b) => b.p_know - a.p_know);

  return (
    <div className="rounded-xl border border-text/10 bg-surface p-4">
      <div className="mb-3 text-[11px] uppercase tracking-widest text-muted">Mastery by topic</div>
      <div className="space-y-3">
        {sorted.map((s) => {
          const pct = Math.round(s.p_know * 100);
          return (
            <div key={s.topic_slug}>
              <div className="font-voice-italic mb-1.5 flex justify-between text-[13px]">
                <span className="text-text/80">{s.topic_slug}</span>
                <span className="font-mono not-italic text-text">{pct}%</span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-base">
                <div
                  className="h-full rounded-full bg-pine transition-all duration-500"
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
        {sorted.length === 0 && (
          <div className="text-xs text-muted">No skill data yet — start a conversation.</div>
        )}
      </div>
    </div>
  );
}
