"""
Joins human_eval_scores_excl_outlier.csv (mean human ratings per
interaction) with each interaction's extracted_features from the DB,
producing a flat training CSV for the classical scorer.

Run from backend/:
    python build_training_set.py human_eval_scores_excl_outlier.csv
"""

import csv
import sys
import json

from app.database import SessionLocal
from app.models.db_models import Interaction

DIMENSIONS = ["Groundedness", "Correctness", "Clarity", "Pedagogical fit"]
OUTPUT_FILE = "classical_scorer_training_set.csv"


def load_human_scores(scores_csv_path):
    """Returns {interaction_id: {dim: mean_score}}"""
    scores = {}
    with open(scores_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            iid = row["interaction_id"]
            scores[iid] = {
                dim: float(row[f"mean_{dim}"]) if row[f"mean_{dim}"] else None
                for dim in DIMENSIONS
            }
    return scores


def main():
    if len(sys.argv) != 2:
        print("Usage: python build_training_set.py <human_eval_scores.csv>")
        sys.exit(1)

    scores_csv_path = sys.argv[1]
    human_scores = load_human_scores(scores_csv_path)

    db = SessionLocal()

    rows_written = 0
    skipped_no_features = []
    skipped_no_score = []

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as out:
        writer = None

        for iid, scores in human_scores.items():
            interaction = db.query(Interaction).filter(Interaction.id == int(iid)).first()

            if interaction is None:
                skipped_no_score.append(iid)
                continue

            if not interaction.extracted_features:
                skipped_no_features.append(iid)
                continue

            features = interaction.extracted_features
            if isinstance(features, str):
                features = json.loads(features)

            row = {"interaction_id": iid}
            row.update(features)
            for dim in DIMENSIONS:
                row[f"label_{dim}"] = scores[dim]

            if writer is None:
                writer = csv.DictWriter(out, fieldnames=list(row.keys()))
                writer.writeheader()

            writer.writerow(row)
            rows_written += 1

    print(f"Wrote {rows_written} rows to {OUTPUT_FILE}")
    if skipped_no_features:
        print(f"WARNING: {len(skipped_no_features)} interactions had no extracted_features, skipped: {skipped_no_features}")
    if skipped_no_score:
        print(f"WARNING: {len(skipped_no_score)} interaction IDs from the scores CSV weren't found in the DB, skipped: {skipped_no_score}")


if __name__ == "__main__":
    main()