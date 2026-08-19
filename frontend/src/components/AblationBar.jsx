// Side-by-side comparison bar for ablation results (e.g. RAG vs No-RAG on
// one metric). A significance badge makes it immediately clear whether a
// visible gap is actually statistically meaningful -- important here
// specifically because some of this project's ablations show a real gap
// that ISN'T significant (multi-agent accuracy), which is an honest and
// easy-to-misread result if the chart doesn't call it out directly.

export default function AblationBar({ metric, labelA, valueA, labelB, valueB, pValue, maxVal = 1 }) {
  const significant = pValue < 0.05;

  return (
    <div className="rounded-xl border border-muted/20 bg-surface p-4">
      <div className="mb-3 flex items-center justify-between">
        <div className="font-display text-sm font-medium text-text">{metric}</div>
        <span
          className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 font-mono text-[11px] ${
            significant
              ? "border-teal/40 bg-teal/10 text-teal"
              : "border-muted/30 bg-muted/10 text-muted"
          }`}
        >
          <span className="h-1.5 w-1.5 rounded-full bg-current" />
          p {pValue < 0.0001 ? "< 0.0001" : `= ${pValue.toFixed(3)}`}
          {" · "}
          {significant ? "significant" : "not significant"}
        </span>
      </div>

      <div className="space-y-2.5">
        {[
          { label: labelA, value: valueA, color: "bg-teal" },
          { label: labelB, value: valueB, color: "bg-muted" },
        ].map((row) => (
          <div key={row.label}>
            <div className="mb-1 flex justify-between font-mono text-xs">
              <span className="text-muted">{row.label}</span>
              <span className="text-text">{row.value.toFixed(3)}</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-base">
              <div
                className={`h-full rounded-full ${row.color} transition-all duration-700`}
                style={{ width: `${(row.value / maxVal) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
