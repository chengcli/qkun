import yaml
import numpy as np
import os
import asyncio
from typing import Tuple, Optional
from netCDF4 import Dataset
from ..geobox import GeoBox
from ..cmr.granule_download import GranuleDownloader
from ..granule.append_resolution import append_resolution_to_yaml
from ..granule.compute_alpha_envelope import compute_alpha_envelope
from ..granule.granule_handler import GranuleHandler

def read_var_masked(group, var_name, dtype=np.float32):
    var = group.variables[var_name]
    data = var[:].astype(dtype)
    fill_value = var.getncattr("_FillValue") if "_FillValue" in var.ncattrs() else None
    data = np.ma.masked_invalid(data)
    if fill_value is not None:
        data = np.ma.masked_equal(data, fill_value)
    return data

def process_footprint(nc_path: str, yaml_file: str=None, verbose: bool=True) -> Tuple[np.ndarray, np.ndarray]:
    """Extracts latitude and longitude from 'geolocation_data' group and caches to .npz file."""

    path, basename = os.path.split(nc_path)
    output_file = os.path.join(path, f"{os.path.splitext(basename)[0]}.footprint.npz")

    ds = Dataset(nc_path, mode="r")

    if "geolocation_data" not in ds.groups:
        raise ValueError("Group 'geolocation_data' not found in NetCDF file.")

    geo_group = ds.groups["geolocation_data"]
    lat = read_var_masked(geo_group, "latitude")
    lon = read_var_masked(geo_group, "longitude")

    if yaml_file is not None:
        append_resolution_to_yaml(lat, lon, yaml_file)
        print(f"Appended resolution to: {yaml_file}")

    # Save both arrays
    np.savez_compressed(output_file, latitude=lat, longitude=lon)
    ds.close()

    if verbose:
        print(f"Footprint data saved to: {output_file}")
    return output_file

class OceanColor(GranuleHandler):
    def __init__(self, digest_path, verbose: bool=False):
        super().__init__("oci", "Ocean Color Instrument", verbose=verbose)
        path, basename = os.path.split(digest_path)
        self.prefix = path
        self.basename = os.path.splitext(os.path.splitext(basename)[0])[0]

    def __del__(self):
        if hasattr(self, "ds"):
            self.ds.close()

    def process(self, alpha: float=0.0, max_points: int=1000):
        digest_path = f"{os.path.join(self.prefix, self.basename)}.global.yaml"
        with open(digest_path, "r") as f:
            digest = yaml.safe_load(f)

        # footprint
        if not os.path.exists(self.footprint_path()):
            nc_file = digest["data_path"]
            if not os.path.exists(nc_file):
                # download data
                downloader = GranuleDownloader(self.USERNAME, self.PASSWORD,
                        self.prefix, verbose=self.verbose)
                url = digest["url_path"]
                asyncio.run(downloader.download(url))
            footprint_path = process_footprint(nc_file, digest_path, self.verbose)
        else:
            footprint_path = self.footprint_path()

        # field of view
        if not os.path.exists(self.fov_path(alpha)):
            compute_alpha_envelope(footprint_path,
                                   alpha, max_points, self.verbose)


        if self.verbose:
            print(f"Processing done: {self.basename}")

    def get_fov(self, alpha: float=0.0) -> Tuple[np.ndarray, np.ndarray]:
        if not os.path.exists(self.fov_path(alpha)):
            raise ValueError(f"FOV file not found: {self.fov_path(alpha)}")

        fov_path = self.fov_path(alpha)
        data = np.genfromtxt(fov_path)
        return data[:, 0], data[:, 1]

    def get_bounding_box(self) -> GeoBox:
        if not os.path.exists(self.digest_path()):
            raise ValueError(f"Digest file not found: {self.digest_path()}")

        digest_path = self.digest_path()
        with open(digest_path, "r") as f:
            digest = yaml.safe_load(f)
        lat_min = digest["geospatial_lat_min"]
        lat_max = digest["geospatial_lat_max"]
        lon_min = digest["geospatial_lon_min"]
        lon_max = digest["geospatial_lon_max"]

        return GeoBox(latmin=lat_min, latmax=lat_max, lonmin=lon_min, lonmax=lon_max)

    def get_footprint(self) -> Tuple[np.ndarray, np.ndarray]:
        if not os.path.exists(self.footprint_path()):
            raise ValueError(f"Footprint file not found: {self.footprint_path()}")

        data = np.load(self.footprint_path())
        return data["longitude"], data["latitude"]

    def get_data(self, name: Optional[str]=None) -> dict:
        if not os.path.exists(self.digest_path()):
            raise ValueError(f"Digest file not found: {self.digest_path()}")

        digest_path = self.digest_path()
        with open(digest_path, "r") as f:
            digest = yaml.safe_load(f)

        nc_file = digest["data_path"]
        if not os.path.exists(nc_file):
            if self.verbose:
                print(f"Downloading data from: {digest['url_path']}")
            # download data
            downloader = GranuleDownloader(self.USERNAME, self.PASSWORD,
                    self.prefix, verbose=self.verbose)
            url = digest["url_path"]
            asyncio.run(downloader.download(url))

        self.ds = Dataset(nc_file, mode="r")

        if "observation_data" not in self.ds.groups:
            raise ValueError("Group 'observation_data' not found in NetCDF file.")
        obs_group = self.ds.groups["observation_data"]

        if name is None:
            return obs_group
        else:
            if name not in obs_group.variables:
                raise ValueError(f"Variable '{name}' not found in Group 'observation_data'.")
            return obs_group.variables[name]
