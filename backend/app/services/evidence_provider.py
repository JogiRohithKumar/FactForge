"""Google Fact Check Tools adapter; review matches are leads, never proof."""
import logging
import requests
from app.core.config import get_settings

logger = logging.getLogger(__name__)
class EvidenceProviderError(RuntimeError):
    pass

class GoogleFactCheckProvider:
    ENDPOINT = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

    def search(self, claim: str) -> list[dict]:
        key = get_settings().google_fact_check_api_key
        if not key:
            return []
        try:
            response = requests.get(
                self.ENDPOINT,
                params={"query": claim, "key": key, "pageSize": 5},
                timeout=(2.0, 3.0),
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.warning("Fact-check provider request failed: %s", type(exc).__name__)
            raise EvidenceProviderError("Evidence search is temporarily unavailable") from exc
        results = []
        for item in payload.get("claims", []):
            for review in item.get("claimReview", []):
                url, title = review.get("url"), review.get("title")
                publisher = (review.get("publisher") or {}).get("name")
                if url and title and publisher:
                    results.append({
                        "publisher": publisher, "title": title, "url": url,
                        "rating": review.get("textualRating"),
                        "review_date": review.get("reviewDate"),
                    })
        return results

provider = GoogleFactCheckProvider()
