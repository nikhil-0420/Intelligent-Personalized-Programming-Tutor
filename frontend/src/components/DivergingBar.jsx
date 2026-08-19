// Diverging bar chart centered at 0 -- built specifically for the classical
// scorer's R^2 results, where negative values (worse than predicting the
// mean) need to read as clearly different from positive ones, not just as
// "a smaller bar."

export default function DivergingBar({ label, value, maxAbs = 0.3 }) {
  const isNegative = value < 0;
  const pct = Math.min(Math.abs(value) / maxAbs, 1) * 50; // half-width max

  return (
    <div className="flex items-center gap-3">
      <div className="w-36 shrink-0 font-mono text-xs text-muted">{label}</div>
      <div className="relative h-6 flex-1">
        {/* center zero-line */}
        <div className="absolute left-1/2 top-0 h-full w-px bg-muted/40" />
        <div className="absolute inset-0 flex items-center">
          <div className="relative h-3 w-full">
            <div
              className={`absolute top-0 h-3 rounded-sm transition-all duration-700 ${
                isNegative ? "right-1/2 bg-amber/70" : "left-1/2 bg-teal/70"
              }`}
              style={{ width: `${pct}%` }}
            />
          </div>
        </div>
      </div>
      <div
        className={`w-16 shrink-0 text-right font-mono text-xs ${
          isNegative ? "text-amber" : "text-teal"
        }`}
      >
        {value >= 0 ? "+" : ""}
        {value.toFixed(3)}
      </div>
    </div>
  );
}
