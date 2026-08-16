"""
Trains one small model per rubric dimension, using Ridge regression
(heavily regularized, far fewer effective parameters than XGBoost) and
a narrowed, theoretically-justified feature set per dimension, since a
10-feature XGBoost model was overfitting/finding spurious patterns at
n=20 (e.g. sentence_count "driving" correctness, which has no real
causal link).

Reports both leave-one-out R^2 and mean absolute error (MAE) -- MAE is
more interpretable and less punishing at small n than R^2.

Run from backend/:
    python train_classical_scorer.py
"""

import pandas as pd
import numpy as np
import shap
from sklearn.linear_model import Ridge
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler

# Narrowed, dimension-specific feature sets -- chosen for what each
# dimension actually measures, not just "throw everything at it."
DIMENSION_FEATURES = {
    "Groundedness": ["max_chunk_similarity", "mean_chunk_similarity", "min_chunk_similarity"],
    "Clarity": ["sentence_count", "avg_sentence_length", "avg_word_length"],
    "Pedagogical fit": ["p_know", "avg_word_length", "technical_term_count"],
    # Correctness genuinely isn't well captured by these structural
    # features -- none of them encode factual accuracy. Kept narrow and
    # flagged as the weakest fit; the LLM judge is the better tool for
    # this dimension specifically, not the classical scorer.
    "Correctness": ["min_chunk_similarity", "technical_term_count"],
}


def train_and_evaluate(df, dimension):
    features = DIMENSION_FEATURES[dimension]
    X = df[features]
    y = df[f"label_{dimension}"]

    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=features)

    loo = LeaveOneOut()
    preds, actuals = [], []

    for train_idx, test_idx in loo.split(X_scaled):
        X_train, X_test = X_scaled.iloc[train_idx], X_scaled.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        model = Ridge(alpha=5.0)  # strong regularization given n=20
        model.fit(X_train, y_train)
        pred = model.predict(X_test)[0]

        preds.append(pred)
        actuals.append(y_test.values[0])

    loo_r2 = r2_score(actuals, preds)
    loo_mae = mean_absolute_error(actuals, preds)
    print(f"\n{dimension} (features: {features})")
    print(f"  leave-one-out R^2  = {loo_r2:.3f}")
    print(f"  leave-one-out MAE  = {loo_mae:.3f}  (avg error, on a 1-5 scale)")

    # Fit on all data for the final model + SHAP explanation
    final_model = Ridge(alpha=5.0)
    final_model.fit(X_scaled, y)

    explainer = shap.LinearExplainer(final_model, X_scaled)
    shap_values = explainer(X_scaled)

    mean_abs_shap = pd.Series(
        np.abs(shap_values.values).mean(axis=0), index=features
    ).sort_values(ascending=False)

    print(f"  Feature importance (mean |SHAP value|):")
    for feat, val in mean_abs_shap.items():
        print(f"    {feat}: {val:.3f}")

    return final_model, loo_r2, loo_mae


def main():
    df = pd.read_csv("classical_scorer_training_set.csv")
    print(f"Loaded {len(df)} labeled interactions.\n")
    print("=" * 60)
    print("TRAINING PER-DIMENSION SCORERS (Ridge, narrowed features, LOO-CV)")
    print("=" * 60)

    results = {}
    for dim in DIMENSION_FEATURES:
        model, loo_r2, loo_mae = train_and_evaluate(df, dim)
        results[dim] = {"r2": loo_r2, "mae": loo_mae}

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for dim, r in results.items():
        print(f"  {dim}: R^2 = {r['r2']:.3f}, MAE = {r['mae']:.3f}")

    print("\nNote: Correctness is the weakest-fit dimension here by design -- "
          "structural/similarity features don't encode factual accuracy well. "
          "Consider relying on the LLM judge for correctness specifically, "
          "and the classical scorer for groundedness/clarity/pedagogical_fit, "
          "where the features have a real theoretical link to the dimension.")


if __name__ == "__main__":
    main()