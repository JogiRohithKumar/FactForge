# utils/text_processor.py
import string
import nltk

try:
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))

def clean_text(text: str) -> str:
    """
    Standardized preprocessing pipeline.
    Ensures inference features perfectly align with the training distribution.
    """
    if not text:
        return ""
    # Lowercase conversion
    text = text.lower()
    # Punctuation removal
    text = ''.join(c for c in text if c not in string.punctuation)
    # Tokenization & Stopword elimination
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)