"""
Statistical significance tests for Phase 12 ablations.
Part A: RAG vs No-RAG (reads rag_ablation_120.csv)
Part B: Multi-agent vs Single-agent, response quality (reads the
        checkpoint file run_multiagent_ablation.py writes)
Part C: Assessor vs Single-agent, assessment accuracy (McNemar's,
        computed automatically from assessment_accuracy_records.jsonl)
"""

import csv
import json
from scipy import stats
from scipy.stats import binomtest


def paired_significance(name, condition_a, condition_b, label_a="A", label_b="B"):
    assert len(condition_a) == len(condition_b), "Lists must be paired (same length)"
    n = len(condition_a)
    mean_a = sum(condition_a) / n
    mean_b = sum(condition_b) / n
    t_stat, p_ttest = stats.ttest_rel(condition_a, condition_b)
    try:
        w_stat, p_wilcoxon = stats.wilcoxon(condition_a, condition_b)
    except ValueError:
        w_stat, p_wilcoxon = float("nan"), float("nan")
    print(f"\n{name} (n={n})")
    print(f"  {label_a} mean = {mean_a:.3f}   {label_b} mean = {mean_b:.3f}   Delta = {mean_a - mean_b:+.3f}")
    print(f"  Paired t-test:  t={t_stat:.3f}, p={p_ttest:.4f}")
    print(f"  Wilcoxon:       W={w_stat:.1f}, p={p_wilcoxon:.4f}")
    print(f"  Significant at alpha=0.05: {'YES' if p_ttest < 0.05 else 'No'}")


def mcnemar_test(name, b, c):
    n_discordant = b + c
    if n_discordant == 0:
        print(f"\n{name}: no discordant pairs, test not applicable.")
        return
    result = binomtest(min(b, c), n_discordant, 0.5, alternative="two-sided")
    print(f"\n{name} (McNemar's exact test)")
    print(f"  Discordant pairs: b={b}, c={c}  (total={n_discordant})")
    print(f"  p = {result.pvalue:.4f}")
    print(f"  Significant at alpha=0.05: {'YES' if result.pvalue < 0.05 else 'No'}")


def load_rag_ablation_csv(path):
    topics, rag_c, rag_p, rag_g, norag_c, norag_p, norag_g = [], [], [], [], [], [], []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            topics.append(row["topic"])
            rag_c.append(int(row["rag_correctness"]))
            rag_p.append(int(row["rag_pedagogical_fit"]))
            rag_g.append(float(row["rag_grounding"]))
            norag_c.append(int(row["norag_correctness"]))
            norag_p.append(int(row["norag_pedagogical_fit"]))
            norag_g.append(float(row["norag_grounding"]))
    return locals()


def load_response_quality_checkpoint(path):
    multi_c, single_c, multi_p, single_p = [], [], [], []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            multi_c.append(rec["multi_scores"]["correctness"])
            single_c.append(rec["single_scores"]["correctness"])
            multi_p.append(rec["multi_scores"]["pedagogical_fit"])
            single_p.append(rec["single_scores"]["pedagogical_fit"])
    return multi_c, single_c, multi_p, single_p


def compute_mcnemar_bc(path):
    b = c = 0  # b: assessor right, single wrong. c: reverse.
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec["assessor_ok"] and not rec["single_ok"]:
                b += 1
            elif rec["single_ok"] and not rec["assessor_ok"]:
                c += 1
    return b, c


if __name__ == "__main__":
    rag_data = load_rag_ablation_csv("rag_ablation_120.csv")
    paired_significance("RAG vs No-RAG: Groundedness", rag_data["rag_g"], rag_data["norag_g"], "RAG", "No-RAG")
    paired_significance("RAG vs No-RAG: Correctness", rag_data["rag_c"], rag_data["norag_c"], "RAG", "No-RAG")
    paired_significance("RAG vs No-RAG: Pedagogical Fit", rag_data["rag_p"], rag_data["norag_p"], "RAG", "No-RAG")

    multi_c, single_c, multi_p, single_p = load_response_quality_checkpoint("response_quality_checkpoint.jsonl")
    paired_significance("Multi vs Single: Correctness", multi_c, single_c, "Multi", "Single")
    paired_significance("Multi vs Single: Pedagogical Fit", multi_p, single_p, "Multi", "Single")

    b, c = compute_mcnemar_bc("assessment_accuracy_records.jsonl")
    mcnemar_test("Assessor vs Single-agent: Assessment Accuracy (all 10 topics)", b, c)