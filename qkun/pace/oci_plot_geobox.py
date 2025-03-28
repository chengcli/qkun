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
    box = oci_geobox(yaml_file)
    print('Latitude bounds:', box.latmin, box.latmax)
    print('Longitude bounds:', box.lonmin, box.lonmax)

    # Get the projection and extent based on the latitude and longitude bounds
    projection, extent = get_projection(box)

    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=projection)

    plot_geobox(ax, box, extent=extent)

    data = np.genfromtxt("PACE_OCI.20250328T002023.L1B.V3.latlon_alpha=0.00.txt")
    lon, lat = data[:, 0], data[:, 1]
    ax.plot(lon, lat, color='blue', linewidth=1,
            transform=ccrs.Geodetic(), label="FOV")

    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python oci_plot_geobox.py <input.yaml>")
        sys.exit(1)
    main(sys.argv[1])
