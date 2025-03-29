import os
import aiohttp
import aiofiles
from pathlib import Path
from aiohttp import ClientSession, BasicAuth
from tqdm.asyncio import tqdm

class GranuleDownloader:
    def __init__(self, username: str, password: str, save_dir: str = "."):
        self.auth = BasicAuth(username, password)
        self.save_dir = Path(save_dir).resolve()
        self.save_dir.mkdir(parents=True, exist_ok=True)

    async def download(self, url: str) -> Path:
        filename = url.split("/")[-1]
        save_path = self.save_dir / filename

        try:
            async with aiohttp.ClientSession(auth=self.auth) as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        raise Exception(f"HTTP {resp.status}: {resp.reason}")

                    total = int(resp.headers.get("Content-Length", 0))
                    pbar = tqdm(total=total, unit='B', unit_scale=True, desc=filename)

                    async with aiofiles.open(save_path, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(8192):
                            await f.write(chunk)
                            pbar.update(len(chunk))

                    pbar.close()
            print(f"✅ Downloaded to: {save_path}")
            return save_path

        except aiohttp.ClientError as e:
            print(f"❌ Connection error: {e}")
        except Exception as e:
            print(f"❌ Failed to download: {e}")

