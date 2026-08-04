"""
Fetches and extracts article text from a user-supplied URL.

SECURITY: the original implementation passed the raw user URL straight to
`requests.get()` / Newspaper3k with no validation, which is a textbook
SSRF vector — a user could point it at cloud metadata endpoints
(169.254.169.254), internal services, or loopback addresses and have the
*server* fetch it on their behalf. This version:
  1. only allows http/https,
  2. resolves the hostname and rejects private/loopback/link-local/
     reserved/multicast IP ranges before connecting,
  3. disables automatic redirect-following and fails closed on any
     redirect rather than silently trusting a hop we haven't validated.

Caveat documented rather than hidden: a DNS-rebinding attack (where the
name resolves to a safe IP at validation time and a private IP at
connect time) is not fully closed by this alone. Fully closing that
requires pinning the resolved IP into the actual socket connection
(e.g. a custom requests Transport/HTTPAdapter). That's a reasonable
next hardening step — flagged in README follow-ups rather than silently
left out.
"""
import ipaddress
import logging
import socket
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_ALLOWED_SCHEMES = {"http", "https"}
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class UnsafeUrlError(ValueError):
    """Raised when a URL fails SSRF safety checks."""


class ExtractionError(ValueError):
    """Raised when the URL is safe but its content can't be extracted."""


def _assert_public_host(hostname: str) -> None:
    try:
        addrinfos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        raise UnsafeUrlError(f"Could not resolve host: {hostname}") from e

    for family, _, _, _, sockaddr in addrinfos:
        ip = ipaddress.ip_address(sockaddr[0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise UnsafeUrlError(
                f"Refusing to fetch a URL that resolves to a non-public address ({ip})"
            )


def _validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise UnsafeUrlError("Only http:// and https:// URLs are allowed")
    if not parsed.hostname:
        raise UnsafeUrlError("URL has no hostname")
    _assert_public_host(parsed.hostname)
    return url


def extract_text_from_url(url: str) -> str:
    """Extracts clean article text from a news URL. Raises UnsafeUrlError or ExtractionError."""
    settings = get_settings()
    validated_url = _validate_url(url)

    # Engine A: Newspaper3k (best quality when it works)
    try:
        from newspaper import Article

        article = Article(validated_url)
        article.download()
        article.parse()
        if article.text.strip():
            return article.text
    except UnsafeUrlError:
        raise
    except Exception as e:  # noqa: BLE001 - deliberately broad: any parser failure should fall through
        logger.info("Newspaper3k extraction failed, falling back to raw HTML parse: %s", e)

    # Engine B: raw HTML parse fallback
    headers = {
        "User-Agent": _UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        response = requests.get(
            validated_url,
            headers=headers,
            timeout=settings.scrape_timeout_seconds,
            allow_redirects=False,  # fail closed rather than trust an unvalidated redirect target
        )
    except requests.exceptions.RequestException as e:
        raise ExtractionError(f"Request to target URL failed: {e}") from e

    if response.is_redirect:
        raise ExtractionError(
            "Target URL returned a redirect; re-submit the final destination URL directly."
        )
    if response.status_code != 200:
        raise ExtractionError(f"Target URL returned status code {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
        element.decompose()

    paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 20]
    text_content = " ".join(paragraphs)

    if not text_content.strip():
        raise ExtractionError("No extractable article text found on the page")

    return text_content
