import argparse
import asyncio
import re
from datetime import datetime, timezone
from qkun.geobox import GeoBox
from qkun.cmr.product_catalog import ProductCatalog
from qkun.cmr.granule_search import GranuleSearcher, get_granule_urls, add_midnight_utc

def validate_time_after(start: str, inp: str):
    """Validate that inp is a time after start"""
    iso_format = "%Y-%m-%dT%H:%M:%SZ"
    pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")

    if not pattern.fullmatch(inp):
        raise ValueError("Time must be in ISO 8601 UTC format: YYYY-MM-DDTHH:MM:SSZ")

    inp_dt = datetime.strptime(inp, iso_format).replace(tzinfo=timezone.utc)
    start_dt = datetime.strptime(start, iso_format).replace(tzinfo=timezone.utc)

    if inp_dt <= start_dt:
        raise ValueError(f"Time must be later than start time: {start}")

def validate_time_before(end: str, inp: str):
    """Validate that inp is a time before end"""
    iso_format = "%Y-%m-%dT%H:%M:%SZ"
    pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")

    if not pattern.fullmatch(inp):
        raise ValueError("Time must be in ISO 8601 UTC format: YYYY-MM-DDTHH:MM:SSZ")

    inp_dt = datetime.strptime(inp, iso_format).replace(tzinfo=timezone.utc)
    end_dt = datetime.strptime(end, iso_format).replace(tzinfo=timezone.utc)

    if inp_dt >= end_dt:
        raise ValueError(f"Time must be earlier than end time: {end}")

def augment_with_cases(strings):
    seen = set()
    augmented = []
    for s in strings:
        for variant in (s, s.upper(), s.lower()):
            if variant not in seen:
                seen.add(variant)
                augmented.append(variant)
    return augmented

async def run_with(concept_id, temporal, box, formats,
                   page_size, max_pages, verbose=True):
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
        for url in get_granule_urls(granule_page, 
                                    augment_with_cases(formats)):
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

    #### Location validation ####

    box = GeoBox(latmin=-90., latmax=90., lonmin=0., lonmax=360.)
    if args.lat and args.lon:
        box = GeoBox(latmin=args.lat[0], latmax=args.lat[1],
                     lonmin=args.lon[0], lonmax=args.lon[1])

    if not args.quiet:
        print(f"Geolocation Bounds: {box}")

    #### Product validation ####

    catalog = ProductCatalog()
    inst, prod = args.product.split('-')
    concept_id = catalog.get_concept_id(f"{args.mission}", inst, prod)

    if not args.quiet:
        print(f"Concept ID for {args.mission} {inst} {prod}: {concept_id}")

    #### Time validation ####

    meta = catalog.get_product_metadata(f"{args.mission}", inst, prod)
    if args.start:
        args.start = add_midnight_utc(args.start)
        if "start-date" in meta:
            validate_time_after(add_midnight_utc(
                meta["start-date"].strftime("%Y-%m-%d")), args.start)
    else:
        if "start-date" in meta:
            args.start = add_midnight_utc(meta["start-date"])

    if args.end:
        args.end = add_midnight_utc(args.end)
        if "end-date" in meta:
            validate_time_before(add_midnight_utc(
                meta["end-date"].strftime("%Y-%m-%d")), args.end)
    else:
        if "end-date" in meta:
            args.end = add_midnight_utc(meta["end-date"])

    temporal = None
    if args.start and args.end:
        temporal = f"{args.start},{args.end}"
    if not args.quiet:
        print(f"Temporal range: {temporal}")

    #### Async run ####

    asyncio.run(run_with(concept_id, temporal, box, meta["formats"],
                         args.page_size, args.max_pages,
                         verbose=not args.quiet))

if __name__ == "__main__":
    main()
