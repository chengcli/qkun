import requests
import argparse
from typing import Tuple, List, Optional
from ..geobox import GeoBox
from .product_catalog import CMRProductCatalog

class CMRGranuleSearch:
    BASE_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"

    def __init__(self, concept_id: str, temporal: Optional[str] = None,
                 bounding_box: Optional[GeoBox] = None, page_size: int = 100,
                 max_pages: Optional[int] = 10):
        self.concept_id = concept_id
        self.temporal = None
        self.bounding_box = None
        self.page_size = page_size or 100
        self.max_pages = max_pages or 10

    def set_temporal_range(self, start: str, end: str):
        """Set time range in ISO 8601 format: 'YYYY-MM-DDTHH:MM:SSZ'"""
        self.temporal = f"{start},{end}"

    def set_bounding_box(self, box: GeoBox):
        """Set bounding box as (W, S, E, N)"""
        self.bounding_box = f"{box.lonmin},{box.latmin},{box.lonmax},{box.latmax}"

    def search(self) -> List[dict]:
        """Search for all granules using current settings with pagination"""
        all_granules = []
        page = 1

        while True:
            params = {
                "collection_concept_id": self.concept_id,
                "page_size": self.page_size,
                "page_num": page,
            }
            if self.temporal:
                params["temporal"] = self.temporal
            if self.bounding_box:
                params["bounding_box"] = self.bounding_box

            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            entries = data.get("feed", {}).get("entry", [])

            if not entries:
                break

            all_granules.extend(entries)
            page += 1

        return all_granules

    def get_download_urls(self, granules: List[dict]) -> List[str]:
        """Extract download URLs from granule entries"""
        urls = []
        for granule in granules:
            for link in granule.get("links", []):
                if link.get("rel") == "http://esipfed.org/ns/fedsearch/1.1/data#":
                    urls.append(link.get("href"))

        # filter only ".hdf" or ".nc" files
        urls = [url for url in urls if url.endswith(('.hdf', '.nc'))]
        return urls

def main():
    parser = argparse.ArgumentParser(description="Search for NASA CMR granules.")
    parser.add_argument("mission", help="Mission name (e.g., 'pace')")
    parser.add_argument("product", help="Data product, format <instrument>-<format> (e.g., 'OCI-L1B')")
    parser.add_argument("--start", help="Start datetime in ISO format (e.g., 2025-03-28T00:00:00Z)")
    parser.add_argument("--end", help="End datetime in ISO format (e.g., 2025-03-28T23:59:59Z)")
    parser.add_argument("--bbox", nargs=4, type=float, metavar=('W', 'S', 'E', 'N'),
                        help="Bounding box as west south east north, (e.g., -10 30 10 50)")
    parser.add_argument("--page-size", type=int, default=100, help="Number of results per page")

    args = parser.parse_args()

    temporal = None
    if args.start and args.end:
        temporal = f"{args.start},{args.end}"

    box = GeoBox(latmin=-90., latmax=90., lonmin=0., lonmax=360.)
    if args.bbox:
        box = GeoBox(latmin=args.bbox[1], latmax=args.bbox[3],
                     lonmin=args.bbox[0], lonmax=args.bbox[2])

    catalog = CMRProductCatalog("products.yaml")
    inst, prod = args.product.split('-')
    concept_id = catalog.get_concept_id(f"{args.mission}", inst, prod)
    print(f"Concept ID for {args.mission} {inst} {prod}: {concept_id}")

    searcher = CMRGranuleSearch(
        concept_id=concept_id,
        temporal=temporal,
        bounding_box=box,
        page_size=args.page_size
    )

    granules = searcher.search()
    print(f"# Found {len(granules)} granules\n")

    for url in searcher.get_download_urls(granules):
        print(url)


if __name__ == "__main__":
    main()

    # Example usage
    concept_id = "C3392966952-OB_CLOUD"
    granule_search = CMRGranuleSearch(concept_id)
    
    # Set temporal range (example: last 30 days)
    granule_search.set_temporal_range("2025-03-26T00:00:00Z", "2025-03-27T00:00:00Z")
    
    # Set bounding box (example: a region)
    granule_search.set_bounding_box(-10.0, 30.0, 10.0, 50.0)
    print('bounding box:', granule_search.bounding_box)
    
    # Perform search
    granules = granule_search.search()
    
    # Get download URLs
    download_urls = granule_search.get_download_urls(granules)
    
    print(f"Found {len(download_urls)} download URLs:")
    for url in download_urls:
        print(url)
