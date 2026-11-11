"""Canonical text normalization shared by training and inference."""
import re
import string

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "so", "of", "to",
    "in", "on", "at", "by", "for", "with", "about", "as", "is", "are",
    "was", "were", "be", "been", "being", "this", "that", "these", "those",
    "it", "its", "it's", "he", "she", "they", "we", "you", "i", "his",
    "her", "their", "our", "your", "from", "into", "over", "after",
    "before", "than", "not", "no", "will", "would", "can", "could",
    "should", "has", "have", "had", "do", "does", "did", "up", "out",
}

_TRANSLATION = str.maketrans("", "", string.punctuation)

def normalize_text(value: str) -> str:
    """Match the project's demo-training preprocessing exactly."""
    if not isinstance(value, str):
        raise TypeError("text must be a string")
    value = value.lower().translate(_TRANSLATION)
    return re.sub(r"\s+", " ", " ".join(t for t in value.split() if t not in STOPWORDS)).strip()
