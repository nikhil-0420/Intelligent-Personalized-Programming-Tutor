import { Link } from "react-router-dom";

const STATS = [
  { value: "10", label: "topics", tone: "pine" },
  { value: "340", label: "human ratings", tone: "pine" },
  { value: "120", label: "ablation cases", tone: "pine" },
  { value: "3", label: "agents", tone: "clay" },
];

export default function HomePage() {
  return (
    <div className="rounded-xl border border-text/10 bg-surface">
      <div className="px-6 pb-10 pt-16 text-center">      
        <svg width="100%" height="60" viewBox="0 0 600 60" className="mx-auto mb-2 max-w-md">
          <path
            d="M0,30 Q30,10 60,30 T120,30 Q150,50 180,30 T240,30 Q270,15 300,30 T360,30 Q390,45 420,30 T480,30 Q510,12 540,30 T600,30"
            fill="none"
            stroke="#2F5233"
            strokeWidth="1.5"
            opacity="0.5"
          />
        </svg>
        <div className="font-voice-italic mb-2 text-[13px] text-clay">reasoning made visible</div>
        <h1 className="font-display mb-3 text-[34px] font-bold leading-tight text-text">
          A tutor that shows
          <br />
          its work
        </h1>
        <p className="mx-auto mb-6 max-w-md text-sm text-muted">
          Every explanation is traced through retrieval, assessment, and grounding — nothing is a
          black box.
        </p>
        <div className="flex justify-center gap-3">
          <Link
            to="/chat"
            className="rounded-lg bg-pine px-5 py-2.5 text-[13px] font-medium text-base"
          >
            Start learning
          </Link>
          <Link
            to="/evaluation"
            className="rounded-lg border border-text/25 px-5 py-2.5 text-[13px] text-text"
          >
            View evaluation
          </Link>
        </div>
      </div>

      <div className="flex border-t border-text/10">
        {STATS.map((s, i) => (
          <div
            key={s.label}
            className={`flex-1 py-6 text-center ${i < STATS.length - 1 ? "border-r border-text/10" : ""}`}
          >
            <div className={`font-display text-[22px] font-bold ${s.tone === "clay" ? "text-clay" : "text-pine"}`}>
              {s.value}
            </div>
            <div className="mt-0.5 text-[11px] text-muted">{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
