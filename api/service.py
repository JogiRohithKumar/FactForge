import joblib
import os

# Get the directory where service.py is located
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Construct the absolute path to the model files
model_path = os.path.join(BASE_DIR, 'model', 'fake_news_model.pkl')
vectorizer_path = os.path.join(BASE_DIR, 'model', 'tfidf_vectorizer.pkl')

# Load model artifacts
model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

def get_prediction(text):
    # ... rest of your code stays the same
    cleaned_input = [text.lower()]
    vectorized = vectorizer.transform(cleaned_input)
    prediction = model.predict(vectorized)[0]
    probabilities = model.predict_proba(vectorized)
    confidence = probabilities[0][prediction] * 100
    
    return {
        "is_fake": bool(prediction == 0),
        "confidence": round(confidence, 2)
    }