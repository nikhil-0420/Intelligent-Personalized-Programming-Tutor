// Visual confidence-interval bar for the human eval results. Shows the
// mean as a marker within a shaded CI range, on a fixed 1-5 scale, so
// the "how tight is this interval" story is visible at a glance rather
// than requiring the reader to parse two decimal numbers.

export default function CIBar({ label, mean, ciLow, ciHigh, scaleMax = 5 }) {
  const toPct = (v) => (v / scaleMax) * 100;

  return (
    <div className="rounded-xl border border-muted/20 bg-surface p-4">
      <div className="mb-3 flex items-baseline justify-between">
        <div className="font-display text-sm font-medium text-text">{label}</div>
        <div className="font-mono text-lg text-teal">{mean.toFixed(2)}</div>
      </div>
      <div className="relative h-2 rounded-full bg-base">
        {/* CI range shading */}
        <div
          className="absolute top-0 h-2 rounded-full bg-teal/25"
          style={{
            left: `${toPct(ciLow)}%`,
            width: `${toPct(ciHigh) - toPct(ciLow)}%`,
          }}
        />
        {/* mean marker */}
        <div
          className="absolute top-1/2 h-3.5 w-3.5 -translate-y-1/2 -translate-x-1/2 rounded-full border-2 border-teal bg-base"
          style={{ left: `${toPct(mean)}%` }}
        />
      </div>
      <div className="mt-2 flex justify-between font-mono text-[11px] text-muted">
        <span>95% CI [{ciLow.toFixed(2)}, {ciHigh.toFixed(2)}]</span>
        <span>scale 1–5</span>
      </div>
    </div>
  );
}
