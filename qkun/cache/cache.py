import os
import shutil
import time
from pathlib import Path
from appdirs import user_cache_dir

class LRUCacheManager:
    def __init__(self, cache_dir=None, max_cache_size=1 * 1024**3):  # 1 GB default
        default_dir = Path(user_cache_dir("pacegeo"))
        self.cache_dir = Path(cache_dir) if cache_dir else default_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_cache_size = max_cache_size  # in bytes

    def get_cached_file(self, filename):
        path = self.cache_dir / filename
        if path.exists():
            path.touch()
            return path
        return None

    def save_to_cache(self, filename, source_path):
        dest_path = self.cache_dir / filename
        shutil.copy2(source_path, dest_path)
        dest_path.touch()
        self._enforce_cache_limit()
        return dest_path

    def _enforce_cache_limit(self):
        files = list(self.cache_dir.glob("*"))
        files = [(f, f.stat().st_atime, f.stat().st_size) for f in files if f.is_file()]
        total_size = sum(f[2] for f in files)

        if total_size <= self.max_cache_size:
            return

        files.sort(key=lambda x: x[1])  # sort by access time
        while total_size > self.max_cache_size and files:
            f, _, size = files.pop(0)
            try:
                f.unlink()
                total_size -= size
                print(f"LRUCache: Removed {f.name} to free up space.")
            except Exception as e:
                print(f"Failed to remove cache file {f}: {e}")

    def clear_cache(self):
        shutil.rmtree(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def log_stats(self):
        files = list(self.cache_dir.glob("*"))
        file_infos = [(f, f.stat().st_atime, f.stat().st_size) for f in files if f.is_file()]
        total_size = sum(info[2] for info in file_infos)
        total_files = len(file_infos)

        if not file_infos:
            print(f"LRUCache: Cache is empty in {self.cache_dir}")
            return

        largest = max(file_infos, key=lambda x: x[2])
        oldest = min(file_infos, key=lambda x: x[1])

        print(f"\n📦 LRUCache Stats: {self.cache_dir}")
        print(f"• Total files       : {total_files}")
        print(f"• Total size        : {total_size / 1024**2:.2f} MB")
        print(f"• Max allowed size  : {self.max_cache_size / 1024**2:.2f} MB")
        print(f"• Largest file      : {largest[0].name} ({largest[2] / 1024**2:.2f} MB)")
        print(f"• Oldest file       : {oldest[0].name} (last used: {time.ctime(oldest[1])})")

