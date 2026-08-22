import { useState } from "react";

export default function GroundingBadge({ isGrounded, score }) {
  const [showTip, setShowTip] = useState(false);
  const color = isGrounded
    ? "text-pine border-pine/30 bg-pine/8"
    : "text-clay border-clay/30 bg-clay/8";
  const label = isGrounded ? "grounded" : "ungrounded";

  return (
    <span className="relative mt-2 inline-block">
      <span
        onMouseEnter={() => setShowTip(true)}
        onMouseLeave={() => setShowTip(false)}
        className={`inline-flex cursor-default items-center gap-1.5 rounded-full border px-2.5 py-0.5 font-mono text-[10.5px] ${color}`}
      >
        <span className="h-1.5 w-1.5 rounded-full bg-current" />
        {label} · {score?.toFixed(2)}
      </span>
      {showTip && (
        <div className="font-voice absolute bottom-full left-0 z-10 mb-1.5 w-56 rounded-lg border border-text/10 bg-surface p-2.5 text-[11px] leading-snug text-muted shadow-lg">
          Measures how closely this response's wording overlaps with the retrieved
          curriculum content. A correct, well-reasoned answer can still score lower
          here if it doesn't closely echo the source text.
        </div>
      )}
    </span>
  );
}