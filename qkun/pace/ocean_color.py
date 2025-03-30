import numpy as np
import sys
import os
from typing import Tuple
from netCDF4 import Dataset
from pathlib import Path
from append_resolution import append_resolution_to_yaml
from compute_alpha_envelope import compute_alpha_envelope
from ..granule_handler import GranuleHandler
from ..geobox import GeoBox

def process_footprint(prefix: str, nc_path: str, yaml_file: str=None, verbose: bool=True) -> Tuple[np.ndarray, np.ndarray]:
    """Extracts latitude and longitude from 'geolocation_data' group and caches to .npz file."""

    output_file = f'{CACHE_FOLDER_PATH}/{perfix}.footprint.npz'
    ds = Dataset(nc_path, mode="r")

    if "geolocation_data" not in ds.groups:
        raise ValueError("Group 'geolocation_data' not found in NetCDF file.")

    geo_group = ds.groups["geolocation_data"]

    def read_var_masked(var_name):
        var = geo_group.variables[var_name]
        data = var[:].astype(np.float32)
        fill_value = var.getncattr("_FillValue") if "_FillValue" in var.ncattrs() else None
        data = np.ma.masked_invalid(data)
        if fill_value is not None:
            data = np.ma.masked_equal(data, fill_value)
        return data

    lat = read_var_masked("latitude")
    lon = read_var_masked("longitude")

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
        basename = os.path.basename(digest_path)
        self.prefix = os.path.splitext(basename)[0]
        self.digest_path = digest_path

    def process(self, alpha: float=0.0, max_points: int=1000):
        self.footprint_path = process_footprint(
                self.prefix, nc_file, self.digest_path, self.verbose)
        self.fov_path = compute_alpha_envelope(
                self.footprint_path, alpha, max_points, self.verbose)

    def get_fov(self) -> Tuple[np.ndarray, np.ndarray]:
        """Field of view points"""
        data = np.genfromtxt(self.fov_path)
        return data[:, 0], data[:, 1]

    def get_bounding_box(self) -> GeoBox:
        with open(self.digest, "r") as f:
            digest = yaml.safe_load(f)
        lat_min = digest["geospatial_lat_min"]
        lat_max = digest["geospatial_lat_max"]
        lon_min = digest["geospatial_lon_min"]
        lon_max = digest["geospatial_lon_max"]

        return GeoBox(latmin=lat_min, latmax=lat_max, lonmin=lon_min, lonmax=lon_max)

    def get_footprint(self) -> Tuple[np.ndarray, np.ndarray]:
        data = np.load(self.footprint_path)
        return data["longitude"], data["latitude"]

    def get_data(self) -> dict:
        """Extracts data from 'geophysical_data' group and caches to .npz file."""
        basename = os.path.basename(nc_file)
        output_file = f'{os.path.splitext(basename)[0]}.data.npz'

        ds = Dataset(nc_file, mode="r")

        print(f"Data saved to: {output_file}")
        return {"chlor_a": chlor_a, "sst": sst}
