"""
Parses the Google Forms rating export. Every ROW is treated as one
independent rater (some raters shared an email, so we don't dedupe by
email -- row identity is rater identity here).

Computes:
  1. Mapping sanity-check (column group -> interaction)
  2. Inter-rater agreement per interaction/dimension, ALL raters
  3. Same, EXCLUDING one named outlier rater (by row index) -- for
     reporting the effect of a rater with a stated language barrier
  4. Two merged training CSVs: mean scores WITH and WITHOUT the outlier

Usage:
    python analyze_ratings.py <forms_export.csv> <phase11_rating_sample.csv> [outlier_row_index]

outlier_row_index is 1-based, counting only response rows (not header).
Find it by looking at the printed rater list output first, then re-run
with the index once you know which row is the outlier.
"""

import csv
import sys
import statistics

DIMENSIONS = ["Groundedness", "Correctness", "Clarity", "Pedagogical fit"]
COLS_PER_INTERACTION = len(DIMENSIONS)
FIRST_SCORE_COL = 2  # 0-indexed: col 0 = Timestamp, col 1 = Email


def load_sample_order(sample_path):
    with open(sample_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [(row["interaction_id"], row["student_message"]) for row in reader]


def print_mapping_check(sample_order):
    print("=" * 70)
    print("MAPPING SANITY CHECK")
    print("=" * 70)
    for i, (iid, msg) in enumerate(sample_order):
        col_start = FIRST_SCORE_COL + i * COLS_PER_INTERACTION
        print(f"Group {i+1:2d} (cols {col_start+1}-{col_start+COLS_PER_INTERACTION}): "
              f"interaction_id={iid}  \"{msg[:50]}\"")
    print()


def parse_responses(forms_csv_path, n_interactions):
    with open(forms_csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    expected_cols = FIRST_SCORE_COL + n_interactions * COLS_PER_INTERACTION
    if len(header) != expected_cols:
        print(f"WARNING: header has {len(header)} columns, expected {expected_cols}.")

    responses = []
    for row_idx, row in enumerate(rows, start=1):
        timestamp, email = row[0], row[1]
        scores_by_group = {}
        for i in range(n_interactions):
            col_start = FIRST_SCORE_COL + i * COLS_PER_INTERACTION
            group_scores = {}
            for d_idx, dim in enumerate(DIMENSIONS):
                raw = row[col_start + d_idx].strip()
                group_scores[dim] = int(raw) if raw else None
            scores_by_group[i] = group_scores
        responses.append((row_idx, email, timestamp, scores_by_group))

    return responses


def print_rater_list(responses):
    print("Raters loaded (row_index, email, timestamp):")
    for row_idx, email, timestamp, _ in responses:
        print(f"  Row {row_idx}: {email}  ({timestamp})")
    print()


def compute_inter_rater_agreement(responses, n_interactions, label):
    print("=" * 70)
    print(f"INTER-RATER AGREEMENT -- {label}")
    print("=" * 70)

    high_disagreement = []
    for i in range(n_interactions):
        for dim in DIMENSIONS:
            scores = [r[3][i][dim] for r in responses if r[3][i][dim] is not None]
            if len(scores) < 2:
                continue
            spread = max(scores) - min(scores)
            if spread >= 3:
                high_disagreement.append((i, dim, scores, spread))

    if high_disagreement:
        print(f"\n{len(high_disagreement)} (interaction, dimension) pairs with spread >= 3:")
        for i, dim, scores, spread in high_disagreement:
            print(f"  Group {i+1}, {dim}: scores={scores} (spread={spread})")
    else:
        print("\nNo (interaction, dimension) pairs with spread >= 3.")
    print()

    return len(high_disagreement)


def write_merged_training_csv(responses, sample_order, output_path):
    n = len(sample_order)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["interaction_id", "student_message"] + [f"mean_{d}" for d in DIMENSIONS] + ["n_raters"])

        for i, (iid, msg) in enumerate(sample_order):
            row = [iid, msg]
            n_raters = 0
            for dim in DIMENSIONS:
                scores = [r[3][i][dim] for r in responses if r[3][i][dim] is not None]
                mean_score = round(statistics.mean(scores), 2) if scores else ""
                row.append(mean_score)
                n_raters = len(scores)
            row.append(n_raters)
            writer.writerow(row)

    print(f"Wrote {output_path} -- {n} interactions, {len(responses)} raters.")


def main():
    if len(sys.argv) < 3:
        print("Usage: python analyze_ratings.py <forms_export.csv> <phase11_rating_sample.csv> [outlier_row_index]")
        sys.exit(1)

    forms_csv_path, sample_path = sys.argv[1], sys.argv[2]
    outlier_row_index = int(sys.argv[3]) if len(sys.argv) > 3 else None

    sample_order = load_sample_order(sample_path)
    print_mapping_check(sample_order)

    responses = parse_responses(forms_csv_path, len(sample_order))
    print(f"Loaded {len(responses)} rater responses.\n")
    print_rater_list(responses)

    compute_inter_rater_agreement(responses, len(sample_order), label="ALL RATERS")
    write_merged_training_csv(responses, sample_order, "human_eval_scores_all_raters.csv")

    if outlier_row_index is not None:
        filtered = [r for r in responses if r[0] != outlier_row_index]
        print(f"\nExcluding row {outlier_row_index} ({[r[1] for r in responses if r[0]==outlier_row_index]})\n")
        compute_inter_rater_agreement(filtered, len(sample_order), label="EXCLUDING OUTLIER")
        write_merged_training_csv(filtered, sample_order, "human_eval_scores_excl_outlier.csv")
    else:
        print("No outlier_row_index given -- run again with the row number "
              "(from the rater list above) to get the excluding-outlier comparison.")


if __name__ == "__main__":
    main()