"""
Exports a diverse sample of logged interactions into a CSV formatted for
human rating (phase 11). Raters see the message/response, fill in 4 scores.

Run from backend/:
    python export_rating_sample.py
"""

import csv
import random
from collections import defaultdict

from app.database import SessionLocal
from app.models.db_models import Interaction, Topic

SAMPLE_SIZE = 20
OUTPUT_FILE = "phase11_rating_sample.csv"


def mastery_bucket(p_know: float) -> str:
    if p_know is None:
        return "unknown"
    if p_know < 0.3:
        return "beginner"
    if p_know < 0.7:
        return "partial"
    return "strong"


def select_diverse_sample(interactions: list[Interaction], n: int) -> list[Interaction]:
    """
    Stratified sampling: group by (topic, mastery_bucket, was_correct),
    then round-robin pick across groups so the final sample spans as many
    distinct combinations as possible, rather than clustering on whatever's
    most common in the DB.
    """
    groups = defaultdict(list)
    for i in interactions:
        key = (i.topic_id, mastery_bucket(i.p_know_after), i.was_correct)
        groups[key].append(i)

    for group in groups.values():
        random.shuffle(group)

    selected = []
    group_keys = list(groups.keys())
    idx = 0
    while len(selected) < n and any(groups[k] for k in group_keys):
        key = group_keys[idx % len(group_keys)]
        if groups[key]:
            selected.append(groups[key].pop())
        idx += 1

    return selected[:n]


def run():
    db = SessionLocal()

    # Only rate interactions that actually produced a tutor response
    # (skips BKT-only /attempt-endpoint rows, which have no response to judge)
    interactions = (
        db.query(Interaction)
        .filter(Interaction.tutor_response.isnot(None))
        .filter(Interaction.tutor_response != "[no tutor response yet -- BKT-only phase]")
        .all()
    )

    if not interactions:
        print("No rateable interactions found in the DB. Run some /tutor/interact calls first.")
        return

    print(f"Found {len(interactions)} rateable interactions in DB.")
    sample = select_diverse_sample(interactions, SAMPLE_SIZE)
    print(f"Selected {len(sample)} for the rating sample.")

    topics = {t.id: t.title for t in db.query(Topic).all()}

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "interaction_id",
            "topic",
            "student_message",
            "tutor_response",
            "mastery_level_shown_to_rater",  # bucketed, not raw p_know -- avoids anchoring
            "groundedness_score_1_to_5",
            "correctness_score_1_to_5",
            "pedagogical_fit_score_1_to_5",
            "clarity_score_1_to_5",
            "rater_name",
            "notes_optional",
        ])

        for i in sample:
            writer.writerow([
                i.id,
                topics.get(i.topic_id, "unknown"),
                i.student_input,
                i.tutor_response,
                mastery_bucket(i.p_know_after),
                "", "", "", "",  # blank for rater to fill in
                "",
                "",
            ])

    print(f"Wrote {OUTPUT_FILE} -- ready to hand to raters.")

    # Quick diversity check, printed for your own sanity
    topic_counts = defaultdict(int)
    mastery_counts = defaultdict(int)
    correct_counts = defaultdict(int)
    for i in sample:
        topic_counts[topics.get(i.topic_id, "unknown")] += 1
        mastery_counts[mastery_bucket(i.p_know_after)] += 1
        correct_counts[i.was_correct] += 1

    print("\nSample diversity check:")
    print(f"  Topics: {dict(topic_counts)}")
    print(f"  Mastery levels: {dict(mastery_counts)}")
    print(f"  Correct/incorrect: {dict(correct_counts)}")


if __name__ == "__main__":
    run()