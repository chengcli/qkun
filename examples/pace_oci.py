import os
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from qkun import CACHE_FOLDER_PATH
from qkun.granule import save_to_yaml, load_from_yaml
from qkun.pace import OceanColor
from qkun.geobox import get_projection, add_geobox

def plot_geobox(ax, box, extent=None):
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS)
    ax.gridlines(draw_labels=True)

    if extent is None:
        extent = box

    ax.set_extent([extent.lonmin, extent.lonmax, 
                   extent.latmin, extent.latmax], crs=ccrs.PlateCarree())
    add_geobox(ax, box, crs=ccrs.PlateCarree())

basename = "PACE_OCI.20250326T103301.L1B.V3"
digest_path = os.path.join(CACHE_FOLDER_PATH, f"{basename}.global.yaml")

# create an instance of OceanColor
obs = OceanColor(digest_path, verbose=True)

# print the instance
print(obs)

# create auxiliary files such as footprint and field of view
obs.process()

# you can save the instance to a YAML file
save_to_yaml(obs, f"{basename}.yaml")

# or load it back
obs2 = load_from_yaml(f"{basename}.yaml")

# they should be the same
print(obs2)

# get a bounding box
box = obs2.get_bounding_box()
print('Latitude bounds:', box.latmin, box.latmax)
print('Longitude bounds:', box.lonmin, box.lonmax)

# Get the projection and extent based on the latitude and longitude bounds
projection, extent = get_projection(box)

fig = plt.figure(figsize=(10, 8))
ax = plt.axes(projection=projection)

plot_geobox(ax, box, extent=extent)

lon, lat = obs2.get_fov()
ax.plot(lon, lat, color='blue', linewidth=1,
        transform=ccrs.Geodetic(), label="FOV")

plt.legend()
plt.tight_layout()
plt.show()
