from .cache import LRUCacheManager

cache = LRUCacheManager(max_cache_size=500 * 1024**2)  # 500 MB

def download_if_needed(remote_url, filename):
    cached = cache.get_cached_file(filename)
    if cached:
        print(f"Using cached file: {cached}")
        return cached

    # Download file (example)
    import requests
    response = requests.get(remote_url, stream=True)
    response.raise_for_status()
    temp_path = cache.cache_dir / (filename + ".tmp")

    with open(temp_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    final_path = cache.save_to_cache(filename, temp_path)
    temp_path.unlink(missing_ok=True)
    print(f"Downloaded and cached: {final_path}")
    return final_path
