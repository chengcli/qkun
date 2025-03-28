import yaml
import numpy as np
import netCDF4
import sys
import os
import numpy as np
from pathlib import Path

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance (in km) between two points on Earth."""
    R = 6371.0  # Earth radius in km
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (np.sin(dlat / 2)**2 +
         np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2)
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def append_resolution_to_yaml(lat, lon, yaml_file):
    """Compute pixel resolution from geolocation and append to YAML."""
    # Ensure masking is respected if present
    if isinstance(lat, np.ma.MaskedArray):
        lat_mask = ~lat.mask
    else:
        lat_mask = np.ones_like(lat, dtype=bool)

    if isinstance(lon, np.ma.MaskedArray):
        lon_mask = ~lon.mask
    else:
        lon_mask = np.ones_like(lon, dtype=bool)

    mask = lat_mask & lon_mask

    # Calculate distance between adjacent pixels along scan lines
    dists = []
    for i in range(lat.shape[0]):  # each scan line
        lat_line = lat[i]
        lon_line = lon[i]
        valid = mask[i]
        if np.sum(valid) < 2:
            continue
        lat_line = lat_line[valid]
        lon_line = lon_line[valid]
        d = haversine(lat_line[:-1], lon_line[:-1], lat_line[1:], lon_line[1:])
        dists.append(d)

    if not dists:
        raise ValueError("No valid pixel distances found.")

    all_dists = np.concatenate(dists)
    min_res = float(np.min(all_dists))
    max_res = float(np.max(all_dists))

    # Append to YAML
    with open(yaml_file, "r") as f:
        meta = yaml.safe_load(f)

    meta["spatial_resolution_min_km"] = round(min_res, 3)
    meta["spatial_resolution_max_km"] = round(max_res, 3)

    with open(yaml_file, "w") as f:
        yaml.dump(meta, f, sort_keys=False)

    print(f"Updated YAML with resolution: min={min_res:.3f} km, max={max_res:.3f} km")

def extract_pace_latlon(nc_file, yaml_file=None):
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
        print("Usage: python extract_pace_latlon.py <input.nc> [output.yaml]")
        sys.exit(1)

    if len(sys.argv) == 2:
        extract_pace_latlon(sys.argv[1])
    else:
        extract_pace_latlon(sys.argv[1], sys.argv[2])
