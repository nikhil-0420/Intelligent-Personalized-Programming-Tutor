"""
Generates copy-paste-ready text blocks for building the Google Form,
one block per interaction. Paste each block's message/response into a
new Section's description, then add the 4 linear-scale questions after.

Run from backend/:
    python generate_form_content.py
"""

import csv

INPUT_FILE = "phase11_rating_sample.csv"
OUTPUT_FILE = "form_content.txt"


def run():
    with open(INPUT_FILE, encoding="utf-8") as f, open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, 1):
            out.write(f"--- SECTION {idx} (interaction_id={row['interaction_id']}) ---\n\n")
            out.write(f"Topic: {row['topic']}\n")
            out.write(f"Student's level: {row['mastery_level_shown_to_rater']}\n\n")
            out.write(f"Student message:\n{row['student_message']}\n\n")
            out.write(f"Tutor response:\n{row['tutor_response']}\n\n")
            out.write("=" * 60 + "\n\n")

    print(f"Wrote {OUTPUT_FILE} -- {idx} sections ready to paste into Google Forms.")


if __name__ == "__main__":
    run()