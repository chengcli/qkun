import os
import argparse
import asyncio
from pathlib import Path
from qkun.cmr.granule_download import GranuleDownloader

def parse_selection(selection_str, n):
    """Parses a slice string or comma-separated list into list of indices."""
    selection_str = selection_str.strip()
    if ":" in selection_str:
        parts = [int(p) if p else None for p in selection_str.split(":")]
        return list(range(*slice(*parts).indices(n)))
    else:
        return [int(i) for i in selection_str.split(",") if i.isdigit()]

async def run_with(file_path, selector, save_dir, 
                   username, password, verbose=True):
    urls = Path(file_path).read_text().splitlines()
    n = len(urls)

    downloader = GranuleDownloader(username, password, save_dir,
                                   verbose=verbose)

    selected_urls = []
    selected_indices = parse_selection(selector, n)
    print("selected_indices = ", selected_indices)
    for url in urls:
        selected_urls.extend([urls[i] for i in selected_indices])

    # Remove duplicates and preserve order
    selected_urls = list(dict.fromkeys(selected_urls))
    print("selected_urls = ", selected_urls)

    await asyncio.gather(*(downloader.download(url) for url in selected_urls))


def main():
    parser = argparse.ArgumentParser(description="Download data files from URL list.")
    parser.add_argument("file", help="Input text file with URL and slice/index selector per line")
    parser.add_argument("--select", default="::", 
                        help="Slice or comma-separated list of indices to download, default all")
    parser.add_argument("--save-dir", default=".",
                        help="Directory to save downloaded files, default current directory")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress bar and logging, default False")

    args = parser.parse_args()

    asyncio.run(run_with(args.file, args.select, args.save_dir,
                         os.environ["QKUN_USER"],
                         os.environ["QKUN_PASS"], verbose=not args.quiet))

if __name__ == "__main__":
    main()
