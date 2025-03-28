import os
import shutil
import time
from pathlib import Path

class LRUCacheManager:
    def __init__(self, cache_dir=None, max_cache_size=1 * 1024**3):  # 1 GB default
        self.cache_dir = Path(cache_dir or Path.home() / ".cache" / "pacegeo")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_cache_size = max_cache_size  # in bytes

    def get_cached_file(self, filename):
        """Return full path if cached, and update access time."""
        path = self.cache_dir / filename
        if path.exists():
            path.touch()  # update last access time
            return path
        return None

    def save_to_cache(self, filename, source_path):
        """Save a file to the cache directory and enforce size limit."""
        dest_path = self.cache_dir / filename
        shutil.copy2(source_path, dest_path)
        dest_path.touch()  # update access time
        self._enforce_cache_limit()
        return dest_path

    def _enforce_cache_limit(self):
        """Remove least-recently-used files until under the max cache size."""
        files = list(self.cache_dir.glob("*"))
        files = [(f, f.stat().st_atime, f.stat().st_size) for f in files if f.is_file()]
        total_size = sum(f[2] for f in files)

        if total_size <= self.max_cache_size:
            return

        # Sort files by access time (oldest first)
        files.sort(key=lambda x: x[1])

        while total_size > self.max_cache_size and files:
            f, _, size = files.pop(0)
            try:
                f.unlink()
                total_size -= size
                print(f"LRUCache: Removed {f.name} to free up space.")
            except Exception as e:
                print(f"Failed to remove cache file {f}: {e}")

    def clear_cache(self):
        """Clear all cache files."""
        shutil.rmtree(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

