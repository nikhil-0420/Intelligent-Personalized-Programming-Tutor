import { useState } from "react";
import MasteryBars from "./MasteryBars";
import AssessorReasoningCard from "./AssessorReasoningCard";
import AgentStackTrace from "./AgentStackTrace";

const TABS = [
  { key: "mastery", label: "Mastery" },
  { key: "reasoning", label: "Reasoning" },
  { key: "trace", label: "Trace" },
];

export default function InsightDrawer({ open, onClose, skills, lastTrace }) {
  const [tab, setTab] = useState("mastery");

  return (
    <div
      className="fixed right-0 top-0 z-20 h-full w-[280px] transform border-l border-text/10 bg-surface p-5 shadow-[-8px_0_24px_rgba(33,29,24,0.08)] transition-transform duration-300 ease-out"
      style={{ transform: open ? "translateX(0)" : "translateX(100%)" }}
    >
      <div className="mb-4 flex items-center justify-between">
        <span className="text-[13px] font-medium text-text">Insight</span>
        <button onClick={onClose} className="text-sm text-muted hover:text-text">
          ×
        </button>
      </div>

      <div className="mb-4 flex gap-1 rounded-lg bg-base p-1">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex-1 rounded-md py-1.5 text-[10.5px] transition-colors ${
              tab === t.key ? "bg-surface font-medium text-pine shadow-sm" : "text-muted"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="overflow-y-auto" style={{ maxHeight: "calc(100vh - 160px)" }}>
        {tab === "mastery" && <MasteryBars skills={skills} />}
        {tab === "reasoning" && <AssessorReasoningCard trace={lastTrace} />}
        {tab === "trace" && (
          <AgentStackTrace trace={lastTrace} open={true} onToggle={() => {}} />
        )}
      </div>
    </div>
  );
}
