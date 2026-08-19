import GroundingBadge from "./GroundingBadge";

export default function MessageTrace({ trace }) {
  if (!trace || trace.length === 0) return null;

  const agents = trace.map((f) => f.agent.toUpperCase().slice(0, 3));
  const tutorFrame = trace.find((f) => f.agent === "tutor");

  return (
    <div className="mt-1.5 flex items-center gap-2 pl-0.5">
      <svg width="70" height="14" viewBox="0 0 70 14">
        <path
          d="M0,7 Q10,1 20,7 T40,7 Q50,13 60,7 T70,7"
          fill="none"
          stroke="#2F5233"
          strokeWidth="1.2"
          opacity="0.6"
        />
      </svg>
      <span className="font-mono text-[10px] text-muted">{agents.join(" · ")}</span>
      {tutorFrame?.grounding_score !== undefined && (
        <GroundingBadge
          isGrounded={tutorFrame.grounding_score >= 0.5}
          score={tutorFrame.grounding_score}
        />
      )}
    </div>
  );
}
