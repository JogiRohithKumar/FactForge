"""Optional Tavily web research adapter for candidate-source discovery.

Search results are research leads only. Domain classification is a hint, not
proof that a page is an official or primary source.
"""
import logging
import requests
from urllib.parse import urlparse
from app.core.config import get_settings

logger = logging.getLogger(__name__)
class ResearchProviderError(RuntimeError):
    pass

def classify_domain(url: str) -> str:
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    official_suffixes = (".gov", ".gov.in", ".nic.in", ".edu", ".edu.in")
    if host.endswith(official_suffixes) or host in {"gov.uk", "europa.eu", "who.int"}:
        return "potential_official_source"
    return "other_publisher"

class TavilyResearchProvider:
    ENDPOINT = "https://api.tavily.com/search"

    def search(self, claim: str) -> list[dict]:
        key = get_settings().tavily_api_key
        if not key:
            return []
        try:
            response = requests.post(
                self.ENDPOINT,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"query": claim, "search_depth": "basic", "max_results": 3, "include_raw_content": True},
                timeout=(2.0, 4.0),
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.warning("Research search failed: %s", type(exc).__name__)
            raise ResearchProviderError("Research source search is temporarily unavailable") from exc
        sources = []
        for result in payload.get("results", []):
            url, title = result.get("url"), result.get("title")
            if not url or not title:
                continue
            sources.append({
                "title": title[:300],
                "url": url,
                "snippet": (result.get("raw_content") or result.get("content") or "")[:3000],
                "relevance_score": max(0.0, min(1.0, float(result.get("score") or 0.0))),
                "source_classification": classify_domain(url),
            })
        return sources

research_provider = TavilyResearchProvider()
