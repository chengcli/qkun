# 🌍 QKUN

**Geoinformation Tools & Data Access for Satellite Observations**

`Qkun`, pronaunced as "kun", is a Python package for querying, downloading, caching, and processing Earth observation satellite data.

---

## 🚀 Features

- ✅ **Query satellite data** (current & historical) by **spatial and temporal bounds**
- ✅ **Download observational data** by mission, instrument, and processing level
- ✅ **Local LRU cache** with automatic size limit and on-demand re-download
- ✅ **Digest large data files** into lightweight **YAML summaries** for quick inspection

---

## 📦 Installation

### 🐍 System Requirements
- Python 3.9+
- Linux or macOS
- hdf5, netCDF, and other data format libraries

If you are using `MacOS`, you may need to install `hdf5` and `netCDF` libraries:
```bash
brew install hdf5 netcdf
```

If you are using `Ubuntu`, you may need to install `hdf5` and `netCDF` libraries:
```bash
sudo apt-get install libhdf5-dev libnetcdf-dev
```

If you are using `RedHat`, you may need to install `hdf5` and `netCDF` libraries:
```bash
sudo yum install hdf5 netcdf
```

### 🔗 Install from PyPI:
```bash
pip install pacegeo
```

### 🛠️ Install locally (dev mode)
```bash
git clone https://github.com/yourusername/pacegeo.git
cd pacegeo
pip install -e .
```

---

## 📁 Command-line Usage

### 🌐 Query satellite granules
```bash
search-granule pace OCI-L1B --start 2025-03-26 --end 2025-03-27 --lat -10 10 --lon 30 50
```

### 📦 Download satellite granules
```bash
search-granule pace OCI-L1B --start 2025-03-26 --end 2025-03-27 --lat -10 10 --lon 30 50 --quiet > download_list.txt
download-granule download_list.txt --select ::2 --save-dir ${HOME}/.cache/qkun
```

### 📊 Summarize large data files
```bash
digest-granule download_list.txt --select ::2 --save-dir ${HOME}/.cache/qkun
```

---

## 🛰️ Supported Missions, Instruments & Data Levels
| Mission        | Instrument(s)   | Data Level(s) |
|----------------|------------------|----------------|
| **PACE**       | OCI              | L1A, L1B, L2   |
| **MODIS Aqua** | MODIS            | L1B, L2        |
| **VIIRS**      | VIIRS (JPSS)     | L1B, L2        |
| **Sentinel-3** | OLCI             | L1, L2         |
| *(More coming)*| ...              | ...            |

---

🧹 Caching
By default, all downloaded data are cached locally in:
```bash
~/.cache/qkun/
```

To change the cache directory and size limit, set these global variables:
```bash
import qkun
qkun.CACHE_FOLDER_PATH = '/path/to/cache'
qkun.CACHE_SIZE_LIMIT = 10.  # in GB
```

---

## 🤝 Contributing
Contributions are welcome!
Please open an issue or PR if you’d like to:
- Add new missions/instruments
- Improve download or parsing logic
- Enhance command line tools or add GUI
- Expand test coverage

---

## 📬 Contact
Maintained by @chengcli — feel free to reach out with ideas, feedback, or collaboration proposals.

## 🧠 Example Python API Usage
Assuming that you have already downloaded and digested the data using command-line tools, you can use the following Python API to access the data.

```python
import os
from qkun import CACHE_FOLDER_PATH
from qkun.pace import OceanColor

basename = "PACE_OCI.20250326T103301.L1B.V3"
digest_path = os.path.join(CACHE_FOLDER_PATH, f"{basename}.global.yaml")

# create an instance of OceanColor
obs = OceanColor(digest_path, verbose=True)

# create auxiliary files such as footprint and field of view
# also saved in the cache folder
obs.process()

# get a lat-lon bounding box
box = obs.get_bounding_box()

# get instrument field of view
lon, lat = obs.get_fov()

# get data keys
keys = obs.get_data().variables.keys()

# subsample and average over bands
blue = obs.get_data("rhot_blue")[:,::5,::5].mean(axis=0)
```
