"""
Exports the remaining unrated interactions (excluding the 20 already
rated in phase11_rating_sample.csv) into a Sheets-ready CSV -- rows and
columns instead of Form sections, since building another 20+ section
Form isn't worth the manual effort.

Run from backend/:
    python export_remaining_for_sheets.py
"""

import csv
from collections import defaultdict

from app.database import SessionLocal
from app.models.db_models import Interaction, Topic

ALREADY_RATED_FILE = "phase11_rating_sample.csv"
OUTPUT_FILE = "phase11_batch2_sheets.csv"


def mastery_bucket(p_know: float) -> str:
    if p_know is None:
        return "unknown"
    if p_know < 0.3:
        return "beginner"
    if p_know < 0.7:
        return "partial"
    return "strong"


def load_already_rated_ids(path):
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["interaction_id"] for row in reader}


def run():
    db = SessionLocal()
    already_rated = load_already_rated_ids(ALREADY_RATED_FILE)
    print(f"Already rated: {len(already_rated)} interactions -- excluding these.")

    interactions = (
        db.query(Interaction)
        .filter(Interaction.tutor_response.isnot(None))
        .all()
    )

    remaining = [i for i in interactions if str(i.id) not in already_rated]
    print(f"Remaining unrated interactions: {len(remaining)}")

    topics = {t.id: t.title for t in db.query(Topic).all()}

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "interaction_id",
            "topic",
            "mastery_level",
            "student_message",
            "tutor_response",
            "groundedness_1_to_5",
            "correctness_1_to_5",
            "clarity_1_to_5",
            "pedagogical_fit_1_to_5",
            "rater_name",
        ])

        for i in remaining:
            writer.writerow([
                i.id,
                topics.get(i.topic_id, "unknown"),
                mastery_bucket(i.p_know_after),
                i.student_input,
                i.tutor_response,
                "", "", "", "",
                "",
            ])

    print(f"Wrote {OUTPUT_FILE} -- {len(remaining)} rows ready to paste into a Sheet.")

    topic_counts = defaultdict(int)
    for i in remaining:
        topic_counts[topics.get(i.topic_id, "unknown")] += 1
    print(f"Topic breakdown: {dict(topic_counts)}")


if __name__ == "__main__":
    run()