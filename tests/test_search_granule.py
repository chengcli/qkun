import unittest
import subprocess
import sys
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()

