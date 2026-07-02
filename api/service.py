# api/service.py
import joblib
import os
import nltk
import httpx
from bs4 import BeautifulSoup
from newspaper import Article
from cachetools import TTLCache
from utils.text_processor import clean_text

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, 'model', 'fake_news_model.pkl')
vectorizer_path = os.path.join(BASE_DIR, 'model', 'tfidf_vectorizer.pkl')

model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

# In-Memory Prediction Cache: Stores up to 1000 items, expires entries after 10 minutes (600s)
prediction_cache = TTLCache(maxsize=1000, ttl=600)

async def extract_text_from_url_async(url: str) -> str:
    """Extracts text content from an article URL using non-blocking asynchronous requests."""
    # Try Newspaper3k extraction via an isolated execution loop layer
    try:
        article = Article(url)
        article.download()
        article.parse()
        if article.text.strip():
            return article.text
    except Exception:
        pass

    # Asynchronous Fallback Engine using httpx
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # Use an async client context block to handle connection pools
        async with httpx.AsyncClient(timeout=7.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    element.decompose()
                paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 20]
                text_content = " ".join(paragraphs)
                if text_content.strip():
                    return text_content
        raise ValueError(f"Target URL status code: {response.status_code}")
    except Exception as e:
        raise ValueError(f"Asynchronous Extraction Failure: {str(e)}")

def get_prediction(text: str):
    """Computes real-time inference with internal lookups mapped to an in-memory cache layer."""
    # Hash check input data string to prevent redundant compute loops
    text_hash = hash(text)
    if text_hash in prediction_cache:
        return prediction_cache[text_hash]

    processed_text = clean_text(text)
    if not processed_text.strip():
        processed_text = text.lower()
        
    vectorized = vectorizer.transform([processed_text])

    prediction = int(model.predict(vectorized)[0])
    probabilities = model.predict_proba(vectorized)
    confidence = float(probabilities[0][prediction] * 100)

    feature_names = vectorizer.get_feature_names_out()
    nonzero_indices = vectorized.nonzero()[1]
    input_words = [feature_names[i] for i in nonzero_indices]
    
    importances = model.feature_importances_
    word_weights = []
    
    for idx, word in zip(nonzero_indices, input_words):
        word_weights.append({"word": word, "weight": float(importances[idx])})
        
    top_explanations = sorted(word_weights, key=lambda x: x['weight'], reverse=True)[:5]

    result_payload = {
        "is_fake": bool(prediction == 0),
        "confidence": round(confidence, 2),
        "explanations": top_explanations
    }
    
    # Store output data inside our cache before exiting thread
    prediction_cache[text_hash] = result_payload
    return result_payload