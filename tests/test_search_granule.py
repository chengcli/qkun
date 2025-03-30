import unittest
import subprocess
import sys
import os
import asyncio
from pathlib import Path
from qkun.cmr.granule_download import GranuleDownloader

class TestCMRGranuleCLI(unittest.TestCase):
    def setUp(self):
        # Path to your CLI script (adjust this as needed)
        self.script_path = Path(__file__).resolve().parent.parent / "qkun" / "api" / "search_granule.py"

        # Basic arguments for CLI test
        self.base_args = [
            sys.executable,  # use current Python interpreter
            str(self.script_path),
            "pace",
            "OCI-L1B",
            "--start", "2025-03-26T00:00:00Z",
            "--end", "2025-03-27T00:00:00Z",
            "--bbox", "-160", "-20", "-150", "-10",
            "--page-size", "100",
            "--max-pages", "10"
        ]

    def test_cli_runs_successfully(self):
        """Check that CLI completes without crashing and outputs something reasonable"""
        result = subprocess.run(self.base_args, capture_output=True, text=True)

        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)

        self.assertEqual(result.returncode, 0)
        self.assertIn("granule", result.stdout.lower() or "found" in result.stdout.lower())

    def test_download(self):
        """Check that CLI can download files"""
        result = subprocess.run(self.base_args, capture_output=True, text=True)
        downloader = GranuleDownloader(username=os.environ["QKUN_USER"],
                                       password=os.environ["QKUN_PASS"])
        result = result.stdout.split("\n")
        nc_files = []
        for i in range(len(result)):
            if ".nc" in result[i]:
                nc_files.append(result[i])

        asyncio.run(downloader.download(nc_files[0]))

        #urls = ["...", "...", "..."]
        #await asyncio.gather(*(downloader.download(u) for u in urls))


if __name__ == "__main__":
    unittest.main()

