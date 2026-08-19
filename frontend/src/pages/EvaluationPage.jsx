import CIBar from "../components/CIBar";
import AblationBar from "../components/AblationBar";
import DivergingBar from "../components/DivergingBar";
import JudgeFailureCard from "../components/JudgeFailureCard";

const HUMAN_EVAL = [
  { label: "Groundedness", mean: 4.19, ciLow: 4.08, ciHigh: 4.30 },
  { label: "Correctness", mean: 4.24, ciLow: 4.10, ciHigh: 4.38 },
  { label: "Clarity", mean: 4.21, ciLow: 4.08, ciHigh: 4.32 },
  { label: "Pedagogical fit", mean: 4.34, ciLow: 4.22, ciHigh: 4.47 },
];

const CLASSICAL_SCORER = [
  { label: "Groundedness", value: -0.250 },
  { label: "Pedagogical fit", value: -0.238 },
  { label: "Correctness", value: -0.217 },
  { label: "Clarity", value: 0.192 },
];

function SectionHeader({ eyebrow, title, description }) {
  return (
    <div className="mb-4">
      <div className="font-mono text-xs uppercase tracking-widest text-teal">{eyebrow}</div>
      <h2 className="font-display text-xl font-bold text-text">{title}</h2>
      {description && <p className="mt-1 max-w-2xl text-sm text-muted">{description}</p>}
    </div>
  );
}

export default function EvaluationPage() {
  return (
    <div className="mx-auto max-w-6xl space-y-12 pb-16">      
    {/* Intro */}
      <div className="border-b border-muted/20 pb-6">
        <h1 className="font-display text-3xl font-bold text-text">Evaluation</h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted">
          Three evaluation tiers, in order of methodological rigor, plus two
          ablation studies isolating what each architectural choice actually
          contributes. Negative and non-significant results are reported
          honestly, not smoothed over.
        </p>
      </div>

      {/* Tier 1: Human Eval */}
      <section>
        <SectionHeader
          eyebrow="Tier 1 · Primary result"
          title="Human evaluation"
          description="17 independent raters scored 20 interactions across 4 dimensions (340 total ratings). 95% CIs from a two-level bootstrap (10,000 iterations, resampling both interactions and raters)."
        />
        <div className="grid grid-cols-2 gap-4">
          {HUMAN_EVAL.map((d) => (
            <CIBar key={d.label} label={d.label} mean={d.mean} ciLow={d.ciLow} ciHigh={d.ciHigh} />
          ))}
        </div>
      </section>

      {/* Ablation: RAG vs No-RAG */}
      <section>
        <SectionHeader
          eyebrow="Ablation study · n = 120"
          title="RAG vs. no-RAG"
          description="10 topics × 4 mastery levels × 3 questions each, scored by the automated Mistral judge. RAG's effect is specific to groundedness, not correctness or pedagogy."
        />
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <AblationBar
            metric="Groundedness"
            labelA="RAG"
            valueA={0.742}
            labelB="No-RAG"
            valueB={0.708}
            pValue={0.00001}
          />
          <AblationBar
            metric="Correctness"
            labelA="RAG"
            valueA={0.731}
            labelB="No-RAG"
            valueB={0.719}
            pValue={0.167}
          />
          <AblationBar
            metric="Pedagogical fit"
            labelA="RAG"
            valueA={0.756}
            labelB="No-RAG"
            valueB={0.738}
            pValue={0.059}
          />
        </div>
        <p className="mt-3 text-xs text-muted">
          Per-topic: RAG improves groundedness in 9/10 topics. Sorting is the
          consistent exception (No-RAG 0.747 vs RAG 0.722) — held at both
          n=20 and n=120, likely reflecting strong LLM pretraining coverage
          of classic sorting algorithms.
        </p>
      </section>

      {/* Ablation: Single-agent vs Multi-agent */}
      <section>
        <SectionHeader
          eyebrow="Ablation study · n = 154"
          title="Single-agent vs. multi-agent"
          description="Dedicated Assessor Agent vs. one combined prompt handling both tutoring and assessment, measured on assessment accuracy across all 10 topics."
        />
        <div className="max-w-md">
          <AblationBar
            metric="Assessment accuracy"
            labelA="Multi-agent (Assessor)"
            valueA={0.890}
            labelB="Single-agent"
            valueB={0.838}
            pValue={0.169}
          />
        </div>
        <p className="mt-3 text-xs text-muted">
          A real 5.2-point accuracy gap that McNemar's exact test does not
          confirm as significant at this scale. Per-topic mismatch varies
          widely (σ = 10.2) — Sorting and Trees exceed 26%, Searching and DP
          show 0%. Reported as a directional, not yet significant, finding.
        </p>
      </section>

      {/* Classical scorer */}
      <section>
        <SectionHeader
          eyebrow="Tier 2 follow-up · n = 20"
          title="Classical scorer (Ridge + LOO-CV + SHAP)"
          description="Built to replace the LLM judge on dimensions where it hit a capability ceiling. At the current sample size, results are honestly inconclusive on 3 of 4 dimensions."
        />
        <div className="rounded-xl border border-muted/20 bg-surface p-5">
          <div className="mb-4 flex items-center justify-between font-mono text-[11px] text-muted">
            <span>← worse than predicting the mean</span>
            <span>better than baseline →</span>
          </div>
          <div className="space-y-4">
            {CLASSICAL_SCORER.map((d) => (
              <DivergingBar key={d.label} label={d.label} value={d.value} />
            ))}
          </div>
        </div>
        <p className="mt-3 text-xs text-muted">
          Leave-one-out R². Low MAE (0.14–0.18) is not meaningful evidence of
          fit here — human ratings cluster tightly (≈4.0–4.6), so a naive
          "always predict the mean" baseline would show similarly low MAE.
          Motivates scaling the labeled set beyond n=20 before drawing
          conclusions about viability.
        </p>
      </section>

      {/* Judge capability ceiling */}
      <section>
        <SectionHeader
          eyebrow="Tier 2 · Automated LLM judge"
          title="Why the classical scorer exists"
          description="A concrete, logged example of the capability ceiling that motivated the pivot above."
        />
        <div className="max-w-xl">
          <JudgeFailureCard />
        </div>
      </section>
    </div>
  );
}
