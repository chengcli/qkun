import numpy as np
import netCDF4
import sys
import os
from pathlib import Path
from append_resolution import append_resolution_to_yaml

def oci_extract_latlon(nc_file, yaml_file=None):
    """Extracts latitude and longitude from 'geolocation_data' group and caches to .npz file."""
    basename = os.path.basename(nc_file)
    output_file = f'{os.path.splitext(basename)[0]}.latlon.npz'

    ds = netCDF4.Dataset(nc_file, mode="r")

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

    if yaml_file:
        append_resolution_to_yaml(lat, lon, yaml_file)
        print(f"Appended resolution to: {yaml_file}")

    # Save both arrays
    np.savez_compressed(output_file, latitude=lat, longitude=lon)
    ds.close()

    print(f"Geolocation data saved to: {output_file}")
    return output_file


if __name__ == "__main__":
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("Usage: python oci_extract_latlon.py <input.nc> [output.yaml]")
        sys.exit(1)

    if len(sys.argv) == 2:
        oci_extract_latlon(sys.argv[1])
    else:
        oci_extract_latlon(sys.argv[1], sys.argv[2])
