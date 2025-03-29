import aiohttp
from typing import Tuple, List, Optional

from ..geobox import GeoBox
from .product_catalog import ProductCatalog

class GranuleSearch:
    BASE_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"

    def __init__(self, concept_id: str, temporal: Optional[str] = None,
                 bounds: Optional[GeoBox] = None, page_size: int = 100,
                 max_pages: Optional[int] = 10):
        self.concept_id = concept_id
        self.temporal = temporal
        self.bounds = f"{bounds.lonmin},{bounds.latmin},{bounds.lonmax},{bounds.latmax}"
        self.page_size = page_size or 100
        self.max_pages = max_pages or 10

    def __repr__(self):
        return f"GranuleSearch(concept_id={self.concept_id!r}, temporal={self.temporal!r}, " \
               f"bounds={self.bounds!r}, page_size={self.page_size!r}, " \
               f"max_pages={self.max_pages!r})"

    def set_temporal_range(self, start: str, end: str):
        """Set time range in ISO 8601 format: 'YYYY-MM-DDTHH:MM:SSZ'"""
        self.temporal = f"{start},{end}"

    def set_bounds(self, box: GeoBox):
        """Set bounding box as (W, S, E, N)"""
        self.bounds = f"{box.lonmin},{box.latmin},{box.lonmax},{box.latmax}"

    def _build_params(self, page_num: int) -> dict:
        """Build search parameters for a single page"""
        params = {
            "collection_concept_id": self.concept_id,
            "page_size": self.page_size,
            "page_num": page_num
        }
        if self.temporal:
            params["temporal"] = self.temporal
        if self.bounds:
            params["bounding_box"] = self.bounds
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
