"""Conservative sentence-level claim candidate extraction."""
import re

def extract_claim_candidates(text: str, limit: int = 3) -> list[str]:
    """Return a small set of deduplicated sentence candidates, not verified claims."""
    normalized = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", normalized)
    candidates, seen = [], set()
    for sentence in sentences:
        value = sentence.strip(" \t\r\n\"'“”")
        words = value.split()
        if len(words) < 8 or len(words) > 70:
            continue
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        candidates.append(value)
        if len(candidates) >= limit:
            break
    return candidates
