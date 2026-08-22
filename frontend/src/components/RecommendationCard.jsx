import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getRecommendation } from "../api";

const STUDENT_ID = 1;

export default function RecommendationCard({ compact = false, onSelectTopic }) {
  const [rec, setRec] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    getRecommendation(STUDENT_ID)
      .then(setRec)
      .catch((err) => setError(err.message));
  }, []);

  const handleJumpIn = () => {
    if (onSelectTopic) {
      onSelectTopic(rec.recommended_topic);
    } else {
      navigate("/chat", { state: { initialTopic: rec.recommended_topic } });
    }
  };

  if (error) {
    return (
      <div className="rounded-xl border border-text/10 bg-surface p-4 text-xs text-muted">
        Couldn't load a recommendation right now.
      </div>
    );
  }

  if (!rec) {
    return (
      <div className="rounded-xl border border-text/10 bg-surface p-4 text-xs text-muted">
        Finding what to study next...
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-text/10 bg-surface p-4">
      <div className="mb-2 text-[11px] uppercase tracking-widest text-clay">
        what should I study next?
      </div>
      <div className="font-display mb-1.5 text-lg font-bold capitalize text-text">
        {rec.recommended_topic.replace(/_/g, " ")}
      </div>
      <div className="font-voice-italic mb-3 text-[13px] leading-relaxed text-muted">
        {rec.reasoning}
      </div>
      <button
        onClick={handleJumpIn}
        className="rounded-lg bg-pine px-4 py-2 text-[13px] font-medium text-base"
      >
        Start with this topic →
      </button>
      {!compact && rec.blocked_topics && rec.blocked_topics.length > 0 && (
        <div className="mt-3 border-t border-text/10 pt-3 font-mono text-[11px] text-muted">
          {rec.blocked_topics.length} topic{rec.blocked_topics.length > 1 ? "s" : ""} still locked
          by prerequisites
        </div>
      )}
    </div>
  );
}
