"""Safe, lazy ML inference with training-compatible preprocessing."""
import logging
import threading
import joblib
from app.core.config import get_settings
from app.services.text_preprocessing import normalize_text

logger = logging.getLogger(__name__)

class ModelUnavailableError(RuntimeError):
    """Raised when model artifacts cannot be loaded."""

class _ModelRegistry:
    def __init__(self):
        self._model = None
        self._vectorizer = None
        self._lock = threading.Lock()
        self._load_error = None

    def _load(self):
        settings = get_settings()
        try:
            model = joblib.load(settings.model_path)
            vectorizer = joblib.load(settings.vectorizer_path)
            self._model, self._vectorizer, self._load_error = model, vectorizer, None
            logger.info("ML artifacts loaded from %s", settings.model_path.parent)
        except Exception as exc:
            self._load_error = str(exc)
            logger.exception("Unable to load ML artifacts")

    def ensure_loaded(self):
        if self._model is None or self._vectorizer is None:
            with self._lock:
                if self._model is None or self._vectorizer is None:
                    self._load()
        if self._load_error:
            raise ModelUnavailableError("Prediction model is unavailable") from None
        return self._model, self._vectorizer

    @property
    def is_loaded(self):
        return self._model is not None and self._vectorizer is not None and self._load_error is None

registry = _ModelRegistry()

def get_prediction(text: str) -> dict:
    model, vectorizer = registry.ensure_loaded()
    normalized = normalize_text(text)
    if not normalized:
        raise ValueError("Text contains no usable tokens")
    matrix = vectorizer.transform([normalized])
    predicted = int(model.predict(matrix)[0])
    probabilities = model.predict_proba(matrix)[0]
    score = float(probabilities[predicted]) * 100.0
    return {
        "is_fake": predicted == 0,
        "confidence": round(score, 2),
        "model_signal": "misleading_pattern" if predicted == 0 else "authentic_style_pattern",
        "interpretation": "A language-pattern classifier output; not a factual verification."
    }
