"""
Trains on the SYNTHETIC demo dataset (see generate_demo_data.py) without
requiring nltk, so it can run in network-restricted environments.

For real training on the actual ISOT/Kaggle dataset, use model_training.py
instead (which uses nltk's stopword list) once you have nltk and the real
fake.csv/true.csv in place — see the README for exact steps.
"""
import string
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

ML_DIR = Path(__file__).resolve().parent
DATA_DIR = ML_DIR / "data"
MODEL_OUT_DIR = ML_DIR.parent / "backend" / "app" / "model"

# Small built-in stopword list so this doesn't depend on nltk's download
# (which needs network access this sandbox doesn't have). Swap for
# nltk.corpus.stopwords in model_training.py for the real training run.
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "so", "of", "to",
    "in", "on", "at", "by", "for", "with", "about", "as", "is", "are",
    "was", "were", "be", "been", "being", "this", "that", "these", "those",
    "it", "its", "it's", "he", "she", "they", "we", "you", "i", "his",
    "her", "their", "our", "your", "from", "into", "over", "after",
    "before", "than", "not", "no", "will", "would", "can", "could",
    "should", "has", "have", "had", "do", "does", "did", "up", "out",
}


def clean_text(text: str) -> str:
    text = text.lower()
    text = "".join(c for c in text if c not in string.punctuation)
    tokens = [w for w in text.split() if w not in STOPWORDS]
    return " ".join(tokens)


def main() -> None:
    fake_path = DATA_DIR / "fake.csv"
    true_path = DATA_DIR / "true.csv"
    for p in (fake_path, true_path):
        if not p.exists():
            raise FileNotFoundError(f"{p} not found. Run generate_demo_data.py first.")

    fake_df = pd.read_csv(fake_path)
    true_df = pd.read_csv(true_path)
    fake_df["label"] = 0  # 0 = fake, matches api/services/ml_service.py's contract
    true_df["label"] = 1

    df = pd.concat([fake_df, true_df], ignore_index=True)
    df["content"] = (df["title"].fillna("") + " " + df["text"].fillna("")).apply(clean_text)

    x_train, x_test, y_train, y_test = train_test_split(
        df["content"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    vectorizer = TfidfVectorizer(max_features=5000)
    x_train_vec = vectorizer.fit_transform(x_train)
    x_test_vec = vectorizer.transform(x_test)

    model = LogisticRegression(max_iter=1000)
    model.fit(x_train_vec, y_train)

    y_pred = model.predict(x_test_vec)
    print(classification_report(y_test, y_pred, target_names=["fake", "real"]))
    print(
        "\nNOTE: this accuracy is on synthetic, template-generated data with "
        "very clean class separation — it says nothing about real-world "
        "performance. It only confirms the pipeline (train -> save -> load "
        "-> serve) works end to end."
    )

    MODEL_OUT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_OUT_DIR / "fake_news_model.pkl")
    joblib.dump(vectorizer, MODEL_OUT_DIR / "tfidf_vectorizer.pkl")
    print(f"\nModel and vectorizer saved to {MODEL_OUT_DIR}")


if __name__ == "__main__":
    main()
