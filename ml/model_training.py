"""
Trains the TF-IDF + Logistic Regression classifier and saves the
artifacts that api/services/ml_service.py loads at runtime.

Run from anywhere: `python ml/model_training.py`
Expects ml/data/news_combined.csv (produced by data_preparation.py).

NOTE: keep the scikit-learn version here in sync with backend/requirements.txt.
joblib-pickled sklearn models are NOT guaranteed compatible across
scikit-learn versions, and a mismatch fails silently as an unpickling
error at serve time rather than a training-time error.
"""
import string
from pathlib import Path

import joblib
import nltk
import pandas as pd
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

ML_DIR = Path(__file__).resolve().parent
DATA_PATH = ML_DIR / "data" / "news_combined.csv"
MODEL_OUT_DIR = ML_DIR.parent / "backend" / "app" / "model"


def clean_text(text: str, stop_words: set) -> str:
    text = text.lower()
    text = "".join(c for c in text if c not in string.punctuation)
    tokens = [w for w in text.split() if w not in stop_words]
    return " ".join(tokens)


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"{DATA_PATH} not found. Run data_preparation.py first."
        )

    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))

    df = pd.read_csv(DATA_PATH)
    df["content"] = df["content"].fillna("").apply(lambda t: clean_text(t, stop_words))

    x_train, x_test, y_train, y_test = train_test_split(
        df["content"], df["label"], test_size=0.2, random_state=42
    )

    vectorizer = TfidfVectorizer(max_features=5000)
    x_train_vec = vectorizer.fit_transform(x_train)
    x_test_vec = vectorizer.transform(x_test)

    model = LogisticRegression()
    model.fit(x_train_vec, y_train)

    y_pred = model.predict(x_test_vec)
    print(classification_report(y_test, y_pred))

    MODEL_OUT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_OUT_DIR / "fake_news_model.pkl")
    joblib.dump(vectorizer, MODEL_OUT_DIR / "tfidf_vectorizer.pkl")
    print(f"Model and vectorizer saved to {MODEL_OUT_DIR}")


if __name__ == "__main__":
    main()
