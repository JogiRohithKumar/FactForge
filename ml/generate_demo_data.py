"""
Generates a small SYNTHETIC demo dataset so the training pipeline and API
can be run and tested end-to-end without a real dataset on hand.

IMPORTANT: this is NOT a substitute for real training data. It uses
template-based text about fictional topics/places so there's no risk of
encoding real misinformation narratives. It's good enough to prove the
pipeline works (model trains, saves, loads, predicts) — it is NOT good
enough to make any real accuracy claim. Replace with the real ISOT
Fake.csv/True.csv (see README) before treating this as a working
detector.
"""
import csv
import random
from pathlib import Path

random.seed(42)

DATA_DIR = Path(__file__).resolve().parent / "data"

TOPICS = [
    "the town council", "the regional transit authority", "a local hospital",
    "the state agriculture board", "a university research team",
    "the central bank", "a technology startup", "the fire department",
    "a national sports league", "the weather service", "a school district",
    "the housing authority", "a wildlife conservation group",
    "the department of transportation", "a pharmaceutical company",
]

# Sober, attributed, measured phrasing typical of straight news reporting.
REAL_TEMPLATES = [
    "Officials from {topic} announced on {day} that a new policy will take effect next quarter, "
    "according to a statement released to reporters.",
    "{topic} reported a {pct}% change in its latest quarterly figures, citing data reviewed by "
    "independent analysts.",
    "A spokesperson for {topic} confirmed the decision in an interview, noting that the change "
    "follows months of internal review.",
    "According to meeting minutes published by {topic}, the proposal was approved by a vote of "
    "{a} to {b} after public comment.",
    "{topic} said in a press release that the plan will be implemented gradually, with a full "
    "assessment expected within the next year.",
    "Researchers associated with {topic} published findings in a peer-reviewed journal, noting "
    "several limitations of the study.",
    "The board overseeing {topic} held a public hearing on {day}, where residents raised "
    "questions about funding and timelines.",
    "Data released by {topic} this week shows a modest change compared to the same period last "
    "year, officials said.",
]

# Sensationalist, unattributed, urgency/clickbait phrasing typical of the
# "fake" class in these training sets.
FAKE_TEMPLATES = [
    "You WON'T BELIEVE what {topic} is hiding from the public — insiders say it changes EVERYTHING!!!",
    "SHOCKING: {topic} secretly planned this for YEARS and nobody noticed until now, sources claim.",
    "BREAKING: {topic} caught in massive cover-up, and the mainstream media refuses to report it!",
    "Experts are OUTRAGED after leaked documents allegedly prove {topic} lied to everyone all along.",
    "This one weird trick used by {topic} has officials scrambling to explain themselves before it's too late.",
    "{topic} doesn't want you to know this ONE SECRET that will change how you see everything forever.",
    "Anonymous whistleblower reveals {topic} has been manipulating the numbers this whole time, allegedly.",
    "People are FURIOUS after finding out what {topic} really did behind closed doors — share before it's deleted!",
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "a recent weekday"]


def make_row(template: str, topic: str) -> str:
    return template.format(
        topic=topic,
        day=random.choice(DAYS),
        pct=random.randint(1, 40),
        a=random.randint(3, 9),
        b=random.randint(1, 3),
    )


def main(n_per_class: int = 250) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    fake_path = DATA_DIR / "fake.csv"
    true_path = DATA_DIR / "true.csv"

    with fake_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "text"])
        for _ in range(n_per_class):
            topic = random.choice(TOPICS)
            template = random.choice(FAKE_TEMPLATES)
            text = make_row(template, topic)
            writer.writerow([text[:60], text])

    with true_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "text"])
        for _ in range(n_per_class):
            topic = random.choice(TOPICS)
            template = random.choice(REAL_TEMPLATES)
            text = make_row(template, topic)
            writer.writerow([text[:60], text])

    print(f"Wrote {n_per_class} synthetic rows each to {fake_path} and {true_path}")


if __name__ == "__main__":
    main()
