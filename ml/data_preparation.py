"""
Combines the raw fake/true news CSVs into a single labeled dataset.

Run from anywhere: `python ml/data_preparation.py`
Expects ml/data/fake.csv and ml/data/true.csv (download these yourself —
not included in the repo).
"""
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"


def main() -> None:
    fake_path = DATA_DIR / "fake.csv"
    true_path = DATA_DIR / "true.csv"
    for p in (fake_path, true_path):
        if not p.exists():
            raise FileNotFoundError(
                f"Expected input file not found: {p}. "
                "Place fake.csv and true.csv in ml/data/ before running this script."
            )

    fake_df = pd.read_csv(fake_path)
    true_df = pd.read_csv(true_path)

    fake_df["label"] = 0
    true_df["label"] = 1

    df = pd.concat([fake_df, true_df], ignore_index=True)
    df = df[["title", "text", "label"]]
    df["content"] = df["title"].fillna("") + " " + df["text"].fillna("")

    out_path = DATA_DIR / "news_combined.csv"
    df.to_csv(out_path, index=False)
    print(f"Combined data saved to {out_path}")


if __name__ == "__main__":
    main()
