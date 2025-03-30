import argparse
import asyncio
from qkun.geobox import GeoBox
from qkun.cmr.product_catalog import ProductCatalog
from qkun.cmr.granule_search import GranuleSearcher, get_granule_urls, add_midnight_utc

async def run_with(concept_id, temporal, box, page_size, max_pages, verbose=True):
    searcher = GranuleSearcher(
        concept_id=concept_id,
        temporal=temporal,
        bounds=box,
        page_size=page_size,
        max_pages=max_pages
    )

    if verbose:
        print(f"Searching for granules with {searcher}")

    # stream search url
    async for granule_page in searcher.stream():
        if verbose:
            print(f"Got page with {len(granule_page)} granules")
        for url in get_granule_urls(granule_page):
            print(url)

def main():
    parser = argparse.ArgumentParser(description="Search for NASA CMR granules.")
    parser.add_argument("mission", help="Mission name (e.g., 'pace')")
    parser.add_argument("product", help="Data product, format <instrument>-<format> (e.g., 'OCI-L1B')")
    parser.add_argument("--start", 
    help="Start datetime in ISO format, time can be omitted (e.g., 2025-03-28T00:00:00Z, 2025-03-28)")
    parser.add_argument("--end",
    help="End datetime in ISO format, time can be omitted (e.g., 2025-03-28T23:59:59Z, 2025-03-28)")
    parser.add_argument("--lat", nargs=2, type=float, metavar=('S', 'N'),
                        help="Bounding box as south north, (e.g., 30 50)")
    parser.add_argument("--lon", nargs=2, type=float, metavar=('W', 'E'),
                        help="Bounding box as west east, (e.g., -10 10)")
    parser.add_argument("--page-size", type=int, default=100,
                        help="Number of results per page, default 100")
    parser.add_argument("--max-pages", type=int, default=10,
                        help="Maximum number of pages to search, default 10")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress logging, default False")

    args = parser.parse_args()

    temporal = None
    if args.start and args.end:
        temporal = f"{add_midnight_utc(args.start)},{add_midnight_utc(args.end)}"
    if not args.quiet:
        print(f"Temporal range: {temporal}")

    box = GeoBox(latmin=-90., latmax=90., lonmin=0., lonmax=360.)
    if args.lat and args.lon:
        box = GeoBox(latmin=args.lat[0], latmax=args.lat[1],
                     lonmin=args.lon[0], lonmax=args.lon[1])

    if not args.quiet:
        print(f"Geolocation Bounds: {box}")

    catalog = ProductCatalog()
    inst, prod = args.product.split('-')
    concept_id = catalog.get_concept_id(f"{args.mission}", inst, prod)

    if not args.quiet:
        print(f"Concept ID for {args.mission} {inst} {prod}: {concept_id}")

    asyncio.run(run_with(concept_id, temporal, box,
                         args.page_size, args.max_pages,
                         verbose=not args.quiet))

if __name__ == "__main__":
    main()
