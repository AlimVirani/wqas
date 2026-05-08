"""MediaWiki API client and result formatting."""
from dataclasses import dataclass

import requests

_API_URL = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "wiki-qa/0.1 (https://github.com/AlimVirani/wqas; alimv@alumni.ubc.ca)"


@dataclass
class SearchResult:
    title: str
    extract: str


def search(query: str, limit: int = 3) -> list[SearchResult]:
    """Search Wikipedia and return up to *limit* results with plain-text extracts.

    Uses the MediaWiki generator API to fetch titles and lead-section extracts
    in a single round-trip.
    """
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": limit,
        "prop": "extracts",
        "exintro": True,
        "exsentences": 3,
        "explaintext": True,
        "format": "json",
    }
    response = requests.get(_API_URL, params=params, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    data = response.json()

    pages = data.get("query", {}).get("pages", {})
    return [
        SearchResult(title=page.get("title", ""), extract=page.get("extract", ""))
        for page in sorted(pages.values(), key=lambda p: p.get("index", 0))
    ]
