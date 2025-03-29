import aiohttp
import re
import requests
from datetime import datetime, timezone
from typing import Tuple, List, Optional

from ..geobox import GeoBox
from .product_catalog import ProductCatalog

def add_midnight_utc(date_str: str) -> str:
    """
    Takes a date string like '2025-03-28' and returns '2025-03-28T00:00:00Z'
    """
    if 'T' in date_str:
        return date_str
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%dT00:00:00Z")
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format")

def get_granule_urls(granules: List[dict], formats=['.hdf', '.nc']) -> List[str]:
    """Extract download URLs from granule entries"""
    urls = []
    for granule in granules:
        for link in granule.get("links", []):
            if link.get("rel") == "http://esipfed.org/ns/fedsearch/1.1/data#":
                urls.append(link.get("href"))

    # filter only ".hdf" or ".nc" files
    urls = [url for url in urls if url.endswith(tuple(formats))]
    return urls

def validate_temporal(start: str, end: str):
    """Validate that start and end times are ISO 8601 UTC strings and that start < end"""
    iso_format = "%Y-%m-%dT%H:%M:%SZ"
    pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")

    if not (pattern.fullmatch(start) and pattern.fullmatch(end)):
        raise ValueError("Both start and end must be in ISO 8601 UTC format: YYYY-MM-DDTHH:MM:SSZ")

    start_dt = datetime.strptime(start, iso_format).replace(tzinfo=timezone.utc)
    end_dt = datetime.strptime(end, iso_format).replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    if start_dt >= end_dt:
        raise ValueError("Start time must be earlier than end time")

    if end_dt >= now:
        raise ValueError("End time must be earlier than the current time (now)")

def validate_concept_id(concept_id: str):
    """
    Step-1. Validates that the concept_id matches the expected format: C#########-PROVIDER
    Raises ValueError if invalid.
    Step-2. Validates that the concept_id is present in the product catalog.
    """
    pattern = re.compile(r"^C\d{7,}-[A-Z0-9_]+$", re.IGNORECASE)

    if not pattern.fullmatch(concept_id):
        raise ValueError(
            "Invalid concept_id format. Expected format: C#########-PROVIDER (e.g. C2843137325-OB_DAAC)"
        )

    url = f"https://cmr.earthdata.nasa.gov/search/concepts/{concept_id}.json"
    response = requests.get(url)
    return response.status_code == 200

class GranuleSearcher:
    BASE_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"

    def __init__(self, concept_id: str, temporal: Optional[str] = None,
                 bounds: Optional[GeoBox] = None, page_size: int = 100,
                 max_pages: Optional[int] = 10):

        validate_concept_id(concept_id)
        self.concept_id = concept_id

        validate_temporal(*temporal.split(','))
        self.temporal = temporal

        self.bounding_box = f"{bounds.lonmin},{bounds.latmin},{bounds.lonmax},{bounds.latmax}"
        self.page_size = page_size or 100
        self.max_pages = max_pages or 10

    def __repr__(self):
        return f"GranuleSearch(concept_id={self.concept_id!r}, temporal={self.temporal!r}, " \
               f"bounding_box={self.bounding_box!r}, page_size={self.page_size!r}, " \
               f"max_pages={self.max_pages!r})"

    def set_temporal_range(self, start: str, end: str):
        """Set time range in ISO 8601 format: 'YYYY-MM-DDTHH:MM:SSZ'"""
        self.temporal = f"{add_midnight_utc(start)},{add_midnight_utc(end)}"

    def set_bounds(self, box: GeoBox):
        """Set bounding box as (W, S, E, N)"""
        self.bounding_box = f"{box.lonmin},{box.latmin},{box.lonmax},{box.latmax}"

    def _build_params(self, page_num: int) -> dict:
        """Build search parameters for a single page"""
        params = {
            "collection_concept_id": self.concept_id,
            "page_size": self.page_size,
            "page_num": page_num
        }
        if self.temporal:
            params["temporal"] = self.temporal
        if self.bounding_box:
            params["bounding_box"] = self.bounding_box
        return params

    async def _fetch_page(self, session: aiohttp.ClientSession, page_num: int) -> List[dict]:
        """Fetch a single page of granules"""
        params = self._build_params(page_num)
        async with session.get(self.BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get("feed", {}).get("entry", [])

    async def search(self) -> List[dict]:
        """Search for all granules using current settings with pagination"""
        granules = []
        async with aiohttp.ClientSession() as session:
            for page in range(1, self.max_pages + 1):
                entries = await self._fetch_page(session, page)
                if not entries:
                    break
                granules.extend(entries)
        return granules

    async def stream(self):
        """Async generator that yields granules page-by-page"""
        async with aiohttp.ClientSession() as session:
            for page in range(1, self.max_pages + 1):
                entries = await self._fetch_page(session, page)
                if not entries:
                    break
                yield entries  # stream one page at a time
