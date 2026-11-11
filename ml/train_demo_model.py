"""Shared preprocessing training pipeline for synthetic demo data."""
from pathlib import Path
import sys
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
ML_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ML_DIR.parent / "backend"))
from app.services.text_preprocessing import normalize_text
DATA_DIR = ML_DIR / "data"
MODEL_OUT_DIR = ML_DIR.parent / "backend" / "app" / "model"
def main():
    fake_path, true_path = DATA_DIR / "fake.csv", DATA_DIR / "true.csv"
    for path in (fake_path, true_path):
        if not path.exists(): raise FileNotFoundError(f"{path} not found. Run generate_demo_data.py first.")
    fake_df, true_df = pd.read_csv(fake_path), pd.read_csv(true_path)
    fake_df["label"], true_df["label"] = 0, 1
    df = pd.concat([fake_df, true_df], ignore_index=True)
    df["content"] = (df["title"].fillna("") + " " + df["text"].fillna("")).apply(normalize_text)
    x_train, x_test, y_train, y_test = train_test_split(df["content"], df["label"], test_size=0.2, random_state=42, stratify=df["label"])
    vectorizer = TfidfVectorizer(max_features=5000)
    x_train_vec = vectorizer.fit_transform(x_train)
    model = LogisticRegression(max_iter=1000).fit(x_train_vec, y_train)
    print(classification_report(y_test, model.predict(vectorizer.transform(x_test)), target_names=["fake", "real"]))
    print("WARNING: synthetic template accuracy is not a real-world performance estimate.")
    MODEL_OUT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_OUT_DIR / "fake_news_model.pkl")
    joblib.dump(vectorizer, MODEL_OUT_DIR / "tfidf_vectorizer.pkl")
    print(f"Model and vectorizer saved to {MODEL_OUT_DIR}")
if __name__ == "__main__": main()