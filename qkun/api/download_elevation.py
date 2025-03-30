import elevation

def get_cache_path(lat_min, lat_max, lon_min, lon_max, cache_dir):
    """Return a cache path based on bounding box."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"terrain_{lat_min:.2f}_{lat_max:.2f}_{lon_min:.2f}_{lon_max:.2f}.tif"

def download_terrain_data(lon_min, lat_min, lon_max, lat_max, cache_path, use_cache=True):
    """Download or reuse terrain data within the bounding box."""
    if not cache_path.exists() or not use_cache:
        print("Downloading terrain data...")
        elevation.clip(bounds=(lon_min, lat_min, lon_max, lat_max), output=str(cache_path))
    else:
        print(f"Using cached terrain data: {cache_path}")
    return str(cache_path)
