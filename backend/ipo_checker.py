"""
ipo_checker.py

Purpose:
- Check whether a possible SpaceX IPO signal appears in:
  1) SEC EDGAR recent S-1 filings
  2) Nasdaq IPO calendar page / API-like endpoint

How to use:
    pip3 install requests
    python3 ipo_checker.py

In FastAPI, you can import:
    from ipo_checker import check_spacex_ipo
"""

from __future__ import annotations

import re
import json
from datetime import datetime, timezone
from typing import Any, Dict, List

import requests


KEYWORDS = [
    "spacex",
    "space exploration technologies",
    "space exploration technologies corp",
    "space exploration technologies corporation",
    "spcx",
]

SEC_RECENT_S1_ATOM_URL = (
    "https://www.sec.gov/cgi-bin/browse-edgar"
    "?action=getcurrent&type=S-1&owner=include&count=100&output=atom"
)

NASDAQ_IPO_PAGE_URL = "https://www.nasdaq.com/market-activity/ipos"

# This endpoint is not as stable/official as SEC EDGAR.
# It may change or block requests, so the code handles failure safely.
NASDAQ_IPO_API_URL = "https://api.nasdaq.com/api/ipo/calendar?date=upcoming"


def _headers() -> Dict[str, str]:
    """
    SEC asks automated tools to identify themselves with User-Agent.
    Replace the email below with your own email if you want.
    """
    return {
        "User-Agent": "Catherine IPO Watcher yuanjiejiang92@gmail.com",
        "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }


def _contains_keyword(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in KEYWORDS)


def check_sec_recent_s1() -> Dict[str, Any]:
    """
    Checks SEC EDGAR recent S-1 filings Atom feed.
    This is useful because IPO registration statements are often S-1 filings.

    Limitation:
    - If SpaceX files under a slightly different legal name, you may need to add that name
      to KEYWORDS.
    """
    result = {
        "source": "SEC recent S-1 filings",
        "available": False,
        "matches": [],
        "error": None,
    }

    try:
        r = requests.get(SEC_RECENT_S1_ATOM_URL, headers=_headers(), timeout=5)
        r.raise_for_status()
        text = r.text

        if not _contains_keyword(text):
            return result

        # Extract simple matching snippets around keywords
        lower = text.lower()
        snippets: List[str] = []
        for kw in KEYWORDS:
            idx = lower.find(kw)
            if idx != -1:
                start = max(0, idx - 250)
                end = min(len(text), idx + 500)
                snippets.append(text[start:end])

        result["available"] = True
        result["matches"] = snippets[:5]
        return result

    except Exception as e:
        result["error"] = str(e)
        return result


def check_nasdaq_ipo_api() -> Dict[str, Any]:
    """
    Checks Nasdaq's IPO calendar API-like endpoint.

    Limitation:
    - Nasdaq may change this endpoint or block it.
    - Treat this as a helpful signal, not a guaranteed source.
    """
    result = {
        "source": "Nasdaq IPO calendar API-like endpoint",
        "available": False,
        "matches": [],
        "error": None,
    }

    try:
        headers = _headers()
        headers.update({
            "Origin": "https://www.nasdaq.com",
            "Referer": "https://www.nasdaq.com/market-activity/ipos",
        })

        r = requests.get(NASDAQ_IPO_API_URL, headers=headers, timeout=15)
        r.raise_for_status()

        text = r.text
        if not _contains_keyword(text):
            return result

        result["available"] = True

        # Try to parse JSON, but fallback to raw snippets
        try:
            data = r.json()
            result["matches"] = [data]
        except json.JSONDecodeError:
            lower = text.lower()
            snippets = []
            for kw in KEYWORDS:
                idx = lower.find(kw)
                if idx != -1:
                    snippets.append(text[max(0, idx - 250): min(len(text), idx + 500)])
            result["matches"] = snippets[:5]

        return result

    except Exception as e:
        result["error"] = str(e)
        return result


def check_nasdaq_ipo_page() -> Dict[str, Any]:
    """
    Checks the public Nasdaq IPO page text.

    Limitation:
    - Web pages often load data with JavaScript, so the raw HTML may not contain all IPOs.
    """
    result = {
        "source": "Nasdaq IPO calendar public page",
        "available": False,
        "matches": [],
        "error": None,
    }

    try:
        r = requests.get(NASDAQ_IPO_PAGE_URL, headers=_headers(), timeout=15)
        r.raise_for_status()
        text = r.text

        if not _contains_keyword(text):
            return result

        lower = text.lower()
        snippets = []
        for kw in KEYWORDS:
            idx = lower.find(kw)
            if idx != -1:
                snippets.append(text[max(0, idx - 250): min(len(text), idx + 500)])

        result["available"] = True
        result["matches"] = snippets[:5]
        return result

    except Exception as e:
        result["error"] = str(e)
        return result


def check_spacex_ipo() -> Dict[str, Any]:
    """
    Main function for your FastAPI backend.

    Returns:
        {
            "ticker": "SPCX",
            "available": True/False,
            "message": "...",
            "checked_at": "...",
            "sources": [...]
        }
    """
    sources = [
        check_sec_recent_s1(),
        #check_nasdaq_ipo_api(),
        #check_nasdaq_ipo_page(),
    ]

    available_sources = [s for s in sources if s.get("available") is True]
    available = len(available_sources) > 0

    return {
        "ticker": "SPCX",
        "company": "SpaceX / Space Exploration Technologies",
        "available": available,
        "message": (
            "Possible SpaceX IPO signal found. Open Schwab IPO Center now."
            if available
            else "SpaceX IPO signal not found in SEC recent S-1 or Nasdaq IPO calendar."
        ),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
    }


if __name__ == "__main__":
    result = check_spacex_ipo()
    print(json.dumps(result, indent=2, ensure_ascii=False))
