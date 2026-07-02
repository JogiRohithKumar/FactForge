# model_training.py
import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier
from utils.text_processor import clean_text
import os
os.makedirs('model', exist_ok=True)
# 1. System Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
DATA_PATH = os.path.join(BASE_DIR, 'data', 'news_combined.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'model')
os.makedirs(MODEL_DIR, exist_ok=True)

print("Loading combined dataset...")
df = pd.read_csv(DATA_PATH)
df['content'] = df['content'].fillna('').astype(str)

print("Running text cleaning pipeline...")
df['content'] = df['content'].apply(clean_text)

# 2. Split Data
X_train, X_test, y_train, y_test = train_test_split(
    df['content'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
)

# 3. Feature Extraction
print("Vectorizing textual features...")
vectorizer = TfidfVectorizer(max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)

# 4. Production Model Training (XGBoost)
print("Training production XGBoost model classifier...")
model = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    eval_metric='logloss',
    n_jobs=-1
)
model.fit(X_train_vec, y_train)
joblib.dump(model, 'model/fake_news_model.pkl')
joblib.dump(vectorizer, 'model/tfidf_vectorizer.pkl')
print("Model and vectorizer saved successfully inside the model/ directory.")
# 5. Save Model and Vectorizer Weights
model_path = os.path.join(MODEL_DIR, 'fake_news_model.pkl')
vectorizer_path = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')

joblib.dump(model, model_path)
joblib.dump(vectorizer, vectorizer_path)
print(f"Production XGBoost model saved to: {model_path}")
print(f"TF-IDF Vectorizer saved to: {vectorizer_path}")