import sys
import yaml
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from geobox import get_projection, plot_geobox, GeoBox

def oci_geobox(yaml_file_path):
    with open(yaml_file_path, "r") as f:
        oci = yaml.safe_load(f)
    lat_min = oci["geospatial_lat_min"]
    lat_max = oci["geospatial_lat_max"]
    lon_min = oci["geospatial_lon_min"]
    lon_max = oci["geospatial_lon_max"]

    return GeoBox(latmin=lat_min, latmax=lat_max, lonmin=lon_min, lonmax=lon_max)

def main(yaml_file):

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python oci_plot_geobox.py <input.yaml>")
        sys.exit(1)
    main(sys.argv[1])
