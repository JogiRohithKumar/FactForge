import logging
import sys

from app.core.config import get_settings


def configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    # Quiet noisy third-party loggers unless we're actively debugging them.
    for noisy in ("urllib3", "newspaper", "nltk"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
