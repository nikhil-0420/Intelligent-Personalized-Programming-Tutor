"""
Paired significance tests on the RAG vs no-RAG ablation results
(correctness, pedagogical_fit, grounding) from run_rag_ablation.py.
"""

from scipy import stats

# Grounding scores (cosine similarity)
rag_grounding = [0.798, 0.674, 0.781, 0.776, 0.724, 0.752, 0.897, 0.850,
                  0.869, 0.702, 0.788, 0.666, 0.741, 0.726, 0.934, 0.829,
                  0.658, 0.784, 0.798, 0.738]
no_rag_grounding = [0.686, 0.624, 0.750, 0.670, 0.664, 0.690, 0.796, 0.766,
                     0.794, 0.737, 0.828, 0.654, 0.772, 0.642, 0.726, 0.654,
                     0.737, 0.556, 0.800, 0.792]

# Judge correctness scores (1-5)
rag_corr = [5]*20
no_rag_corr = [5,5,5,5, 5,5,5,5, 5,5,5,5, 5,5,5,5, 5,4,5,5]

# Judge pedagogical_fit scores (1-5)
rag_ped = [4]*20
no_rag_ped = [4,4,4,3, 4,4,4,4, 4,4,4,4, 4,4,3,4, 4,4,4,4]


def report(name, rag, no_rag):
    t, p = stats.ttest_rel(rag, no_rag)
    w, wp = stats.wilcoxon(rag, no_rag)
    print(f"\n--- {name} ---")
    print(f"RAG mean: {sum(rag)/len(rag):.3f}  No-RAG mean: {sum(no_rag)/len(no_rag):.3f}")
    print(f"Paired t-test: t={t:.3f}, p={p:.4f}")
    print(f"Wilcoxon:      W={w:.1f}, p={wp:.4f}")


report("Groundedness", rag_grounding, no_rag_grounding)
report("Correctness", rag_corr, no_rag_corr)
report("Pedagogical Fit", rag_ped, no_rag_ped)