import os
import aiohttp
import aiofiles
from typing import Optional
from pathlib import Path
from aiohttp import ClientSession, BasicAuth
from tqdm.asyncio import tqdm

def get_folder_size(path):
    """Returns the total size of the folder in bytes."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(file_path)
            except FileNotFoundError:
                # Skip files that were deleted or inaccessible
                pass
    return total_size

def get_lru_files(path):
    """Returns a list of files sorted by access time (oldest first)."""
    files = []
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                atime = os.stat(file_path).st_atime
                files.append((atime, file_path))
            except FileNotFoundError:
                continue
        break  # Only check the top directory
    files.sort()  # Oldest access time first
    return [f for _, f in files]

class GranuleDownloader:
    def __init__(self, username: str, password: str, save_dir: str = ".",
                verbose: bool = True, max_cache_size: float = 10.0):
        self.auth = BasicAuth(username, password)
        self.save_dir = Path(save_dir).resolve()
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        self.max_cache_size = int(max_cache_size) * 1024**3 # in bytes

    async def download(self, url: str, verbose: Optional[bool] = None) -> Path:
        verbose = self.verbose if verbose is None else verbose
        filename = url.split("/")[-1]
        save_path = self.save_dir / filename

        try:
            async with aiohttp.ClientSession(auth=self.auth) as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP {resp.status}: {resp.reason}")

                    total = int(resp.headers.get("Content-Length", 0))

                    # Make space if needed
                    while get_folder_size(self.save_dir) + total > self.max_cache_size:
                        lru_files = get_lru_files(self.save_dir)
                        if not lru_files:
                            raise RuntimeError("Not enough space in cache and no files to evict.")
                        if verbose:
                            print(f"📦 Cache limit reached. Removing LRU file: {lru_files[0]}")
                            os.remove(lru_files[0])  # Remove LRU file

                    pbar = tqdm(
                            total=total,
                            unit='B',
                            unit_scale=True,
                            desc=filename,
                            disable=not verbose)

                    async with aiofiles.open(save_path, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(8192):
                            await f.write(chunk)
                            pbar.update(len(chunk))

                    pbar.close()

            if verbose:
                current_size = get_folder_size(self.save_dir)
                remaining_space = self.max_cache_size - current_size
                print(f"✅ Downloaded to: {save_path}")
                print(f"📦 Cached data size: {current_size / 1024**3:.2f} GB")
                print(f"📦 Remaining space: {remaining_space / 1024**3:.2f} GB")
            return save_path

        except aiohttp.ClientError as e:
            print(f"❌ Connection error: {e}")
        except Exception as e:
            print(f"❌ Failed to download: {e}")

