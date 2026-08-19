export default function GroundingBadge({ isGrounded, score }) {
  const color = isGrounded
    ? "text-pine border-pine/30 bg-pine/8"
    : "text-clay border-clay/30 bg-clay/8";
  const label = isGrounded ? "grounded" : "ungrounded";

  return (
    <span
      className={`mt-2 inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 font-mono text-[10.5px] ${color}`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {label} · {score?.toFixed(2)}
    </span>
  );
}
