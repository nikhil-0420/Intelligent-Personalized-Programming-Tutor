import { AlertTriangle } from "lucide-react";

// Concrete, logged example of the LLM judge's capability ceiling -- shown
// as a transcript-style card (matching AgentStackTrace's visual language)
// rather than just stating the finding in prose. Seeing the actual
// fabricated claim scored 5/5 is far more convincing than a summary.

export default function JudgeFailureCard() {
  return (
    <div className="rounded-xl border border-amber/30 bg-surface p-4">
      <div className="mb-3 flex items-center gap-2">
        <AlertTriangle size={16} className="text-amber" />
        <div className="font-display text-sm font-medium text-text">
          Logged failure case — Groundedness judge
        </div>
      </div>

      <div className="rounded-lg border border-muted/20 bg-base p-3 font-mono text-xs">
        <div className="text-muted">tutor_response (excerpt):</div>
        <div className="mt-1 text-text">
          "...Alan Turing first proposed this technique in 1954 while working
          on early compiler design at Cambridge..."
        </div>
        <div className="mt-2 text-amber">⚠ fabricated — no such claim exists in any retrieved chunk</div>
      </div>

      <div className="mt-3 flex items-center justify-between rounded-lg border border-amber/30 bg-amber/10 px-3 py-2">
        <span className="font-mono text-xs text-muted">judge_score.groundedness</span>
        <span className="font-mono text-sm font-medium text-amber">5 / 5</span>
      </div>

      <div className="mt-3 text-xs leading-relaxed text-muted">
        This score held across all 3 rounds of prompt iteration (basic → 2
        examples → 5 examples with explicit "don't average partial credit"
        rule). Concluded as a genuine capability ceiling for a 7B judge
        model, not a prompt-wording problem — directly motivated the pivot
        to a classical ML scorer for groundedness and clarity.
      </div>
    </div>
  );
}
