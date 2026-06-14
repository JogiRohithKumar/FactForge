import joblib
import os
import nltk
from newspaper import Article

# Force-download required NLTK tokenization packages for the scraping engine
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Get the directory where service.py is located
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Construct the absolute path to the model files
model_path = os.path.join(BASE_DIR, 'model', 'fake_news_model.pkl')
vectorizer_path = os.path.join(BASE_DIR, 'model', 'tfidf_vectorizer.pkl')

# Load model artifacts
model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

def extract_text_from_url(url: str) -> str:
    """Extracts clean body text from a news URL."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        raise ValueError(f"Failed to parse URL: {str(e)}")

def get_prediction(text):
    cleaned_input = [text.lower()]
    vectorized = vectorizer.transform(cleaned_input)
    
    prediction = model.predict(vectorized)[0]
    probabilities = model.predict_proba(vectorized)
    confidence = probabilities[0][prediction] * 100
    
    return {
        "is_fake": bool(prediction == 0),
        "confidence": round(confidence, 2)
    }