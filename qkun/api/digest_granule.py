import os
import argparse
from pathlib import Path
from ..nc.nc_global_to_yaml import parse_nc_global_attributes, save_to_yaml
from .download_granule import parse_selection

def run_with(file_path, selector, save_dir, verbose=True):
    urls = Path(file_path).read_text().splitlines()

    selected_urls = []
    selected_indices = parse_selection(selector, len(urls))
    for url in urls:
        selected_urls.extend([urls[i] for i in selected_indices])

    # remove duplicates and preserve order
    selected_urls = list(dict.fromkeys(selected_urls))
    if verbose:
        print("selected_urls = ")
        for url in selected_urls:
            print(url)

    for url in selected_urls:
        basename = os.path.basename(url)
        nc_file = os.path.join(f"{save_dir}", basename)

        nc_path = Path(nc_file)
        if not nc_path.exists():
            print(f"Error: NetCDF file '{nc_path}' does not exist.")
            sys.exit(1)

        yaml_path = os.path.join(f"{save_dir}/{os.path.splitext(basename)[0]}.global.yaml")
        attrs = parse_nc_global_attributes(nc_path)

        # append data url
        attrs["url_path"] = url
        attrs["data_path"] = nc_path.as_posix()
        save_to_yaml(attrs, yaml_path)

        if verbose:
            print(f"YAML digest saved to: {yaml_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Create digest files from downloaded data files.")
    parser.add_argument("file", help="Input text file with URL and slice/index selector per line")
    parser.add_argument("--select", default="::", 
                        help="Slice or comma-separated list of indices to download, default all")
    parser.add_argument("--save-dir", default=".",
                        help="Directory to save downloaded files, default current directory")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress bar and logging, default False")

    args = parser.parse_args()

    run_with(args.file, args.select, args.save_dir, verbose=not args.quiet)

if __name__ == "__main__":
    main()
