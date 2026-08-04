"""
Model loading and inference.

The original codebase called joblib.load(...) at *import* time with no
error handling, so a missing/incompatible model file crashed the whole
process before FastAPI even started, and the Streamlit fallback's
`except ImportError` never caught it. Here the model is loaded lazily
and defensively on first use (and cached), so:
  - the app boots even if the model isn't there yet
  - GET /health can report model_loaded=False instead of the process
    being dead
  - a bad model file raises a clean, catchable ModelUnavailableError
    instead of taking down the server
"""
import logging
import threading

import joblib

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ModelUnavailableError(RuntimeError):
    """Raised when the model/vectorizer can't be loaded or used."""


class _ModelRegistry:
    def __init__(self) -> None:
        self._model = None
        self._vectorizer = None
        self._lock = threading.Lock()
        self._load_error: str | None = None

    def _load(self) -> None:
        settings = get_settings()
        try:
            self._model = joblib.load(settings.model_path)
            self._vectorizer = joblib.load(settings.vectorizer_path)
            self._load_error = None
            logger.info("Model and vectorizer loaded from %s", settings.model_path.parent)
        except FileNotFoundError as e:
            self._load_error = f"Model artifacts not found: {e}"
            logger.error(self._load_error)
        except Exception as e:  # noqa: BLE001 - want to surface any load failure the same way
            self._load_error = f"Failed to load model artifacts: {e}"
            logger.exception("Model load failed")

    def ensure_loaded(self):
        if self._model is None or self._vectorizer is None:
            with self._lock:
                if self._model is None or self._vectorizer is None:
                    self._load()
        if self._load_error:
            raise ModelUnavailableError(self._load_error)
        return self._model, self._vectorizer

    @property
    def is_loaded(self) -> bool:
        return self._model is not None and self._vectorizer is not None and self._load_error is None


registry = _ModelRegistry()


def get_prediction(text: str) -> dict:
    """Run inference on raw text. Raises ModelUnavailableError if the model can't be loaded."""
    model, vectorizer = registry.ensure_loaded()

    cleaned_input = [text.lower()]
    vectorized = vectorizer.transform(cleaned_input)

    prediction = model.predict(vectorized)[0]
    probabilities = model.predict_proba(vectorized)
    confidence = float(probabilities[0][prediction] * 100)

    return {
        "is_fake": bool(prediction == 0),
        "confidence": round(confidence, 2),
    }
