import argparse
import asyncio
import re
import os
import yaml
import numpy as np
from pathlib import Path
from itertools import chain
from typing import List, Optional
from datetime import datetime, timezone
from qkun import CACHE_IMAGE_PATH, CACHE_DIGEST_PATH
from qkun.geobox import GeoBox
from qkun.cmr.product_catalog import ProductCatalog
from qkun.cmr.granule_download import GranuleDownloader
from qkun.cmr.granule_search import (
        GranuleSearcher,
        get_granule_urls,
        get_granule_thumbnails,
        get_granule_polygons,
        add_midnight_utc
        )

def find_earliest_date(dates):
    if not dates:
        return None
    return min(dates) if not None in dates else None

def find_latest_date(dates):
    if not dates:
        return None
    return max(dates) if not None in dates else None

def augment_with_cases(strings):
    seen = set()
    augmented = []
    for s in strings:
        for variant in (s, s.upper(), s.lower()):
            if variant not in seen:
                seen.add(variant)
                augmented.append(variant)
    return augmented

def remove_extension(filename, num):
    parts = filename.split(".")
    if len(parts) >= 3:
        # Remove second-from-last extension
        parts.pop(num)
        new_filename = ".".join(parts)
    else:
        new_filename = filename  # unchanged if not enough parts
    return new_filename

async def run_with(concept_id, temporal, box, formats,
                   page_size, max_pages, verbose=True, 
                   download_thumb=False):
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
        basenames = []
        for url in get_granule_urls(granule_page,
                                    augment_with_cases(formats)):
            basenames.append(url.split('/')[-1])
            print(url)

        # save digest
        for i, granule in enumerate(granule_page):
            basename = remove_extension(basenames[i], -1) + '.yaml'
            save_dir = Path(f'{CACHE_DIGEST_PATH}/{temporal}/').resolve()
            save_dir.mkdir(parents=True, exist_ok=True)
            with open(f'{save_dir}/{basename}', 'w') as f:
                yaml.dump(granule, f, sort_keys=False, default_flow_style=False)

        # save thumbnail
        if download_thumb:
            save_dir = f'{CACHE_IMAGE_PATH}/{temporal}/'
            if os.path.exists(save_dir): # Skip if already downloaded
                continue

            downloader = GranuleDownloader("", "", save_dir, verbose=False)
            print(f"Downloading thumbnails to {save_dir} ...")
            await asyncio.gather(*(downloader.download(url)
                                   for url in get_granule_thumbnails(granule_page)))

def main():
    parser = argparse.ArgumentParser(description="Search for NASA CMR granules.")
    parser.add_argument("mission", help="Lower case mission name (e.g., 'pace')")
    parser.add_argument("product", help="Data product, format <instrument>-<level> (e.g., 'OCI-L1B')")
    parser.add_argument("--start", help="Start date in ISO format (e.g., 2025-03-28)")
    parser.add_argument("--end", help="End date in ISO format (e.g., 2025-03-28)")
    parser.add_argument("--lat", nargs=2, type=float, metavar=('S', 'N'),
                        default=[-90., 90.], help="Bounding box as south north, (e.g., 30 50)")
    parser.add_argument("--lon", nargs=2, type=float, metavar=('W', 'E'),
                        default=[-180., 180.], help="Bounding box as west east, (e.g., -10 10)")
    parser.add_argument("--page-size", type=int, default=100,
                        help="Number of results per page, default 100")
    parser.add_argument("--max-pages", type=int, default=10,
                        help="Maximum number of pages to search, default 10")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress logging, default False")
    parser.add_argument('--download-thumb', action='store_true',
                        help="Download thumbnail")

    args = parser.parse_args()

    #### Location validation ####

    box = GeoBox(latmin=-90., latmax=90., lonmin=0., lonmax=360.)
    if args.lat and args.lon:
        box = GeoBox(latmin=args.lat[0], latmax=args.lat[1],
                     lonmin=args.lon[0], lonmax=args.lon[1])

    if not args.quiet:
        print(f"Geolocation Bounds: {box}")

    #### Time validation ####
    catalog = ProductCatalog()
    inst, prod = args.product.split('-')

    meta = catalog.get_products_metadata(f"{args.mission}", inst, prod)
    iso_format = "%Y-%m-%d"
    if args.start:
        start_dt = datetime.strptime(args.start, iso_format).date()
        if find_earliest_date(meta.get("start-date")):
            if start_dt < find_earliest_date(meta["start-date"]):
                raise ValueError("Start time must be later than the earliest start time")
    else:
        start_dt = find_earliest_date(meta.get("start-date"))

    if args.end:
        end_dt = datetime.strptime(args.end, iso_format).date()
        if find_latest_date(meta.get("end-date")):
            if end_dt > find_latest_date(meta["end-date"]):
                raise ValueError("End time must be earlier than the latest end time")
    else:
        end_dt = find_latest_date(meta.get("end-date"))

    temporal = None
    if start_dt and end_dt:
        temporal = f"{start_dt.strftime(iso_format)},{end_dt.strftime(iso_format)}"
    if not args.quiet:
        print(f"Temporal range: {temporal}")

    #### Product validation ####
    concept_id = catalog.get_concept_id(f"{args.mission}", inst, prod,
                                        temporal=temporal)
    if not concept_id:
        raise ValueError(f"Could not find concept ID for {args.mission} {inst} {prod}")

    if not args.quiet:
        print(f"Concept ID for {args.mission} {inst} {prod}: {concept_id}")

    #### Async run ####

    temporal = ','.join([add_midnight_utc(t) for t in temporal.split(',')])
    asyncio.run(run_with(concept_id, temporal, box, 
                         list(chain.from_iterable(meta["formats"])),
                         args.page_size, args.max_pages,
                         verbose=not args.quiet,
                         download_thumb=args.download_thumb))

if __name__ == "__main__":
    main()
