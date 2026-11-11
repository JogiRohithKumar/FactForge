"""Train the baseline classifier with the same normalization used at inference."""
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
DATA_PATH = ML_DIR / "data" / "news_combined.csv"
MODEL_OUT_DIR = ML_DIR.parent / "backend" / "app" / "model"
def main():
    if not DATA_PATH.exists(): raise FileNotFoundError(f"{DATA_PATH} not found. Run data_preparation.py first.")
    df = pd.read_csv(DATA_PATH)
    df["content"] = df["content"].fillna("").apply(normalize_text)
    x_train, x_test, y_train, y_test = train_test_split(df["content"], df["label"], test_size=0.2, random_state=42, stratify=df["label"])
    vectorizer = TfidfVectorizer(max_features=5000)
    x_train_vec = vectorizer.fit_transform(x_train)
    model = LogisticRegression(max_iter=1000).fit(x_train_vec, y_train)
    print(classification_report(y_test, model.predict(vectorizer.transform(x_test))))
    MODEL_OUT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_OUT_DIR / "fake_news_model.pkl")
    joblib.dump(vectorizer, MODEL_OUT_DIR / "tfidf_vectorizer.pkl")
    print(f"Model and vectorizer saved to {MODEL_OUT_DIR}")
if __name__ == "__main__": main()