import os
import asyncio
import yaml
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

from cartopy.feature import ShapelyFeature
from shapely.geometry import Polygon
from qkun import (
        find_image,
        find_all_digests,
        get_basename
        )
from qkun.cmr.granule_search import parse_polygon
from qkun.feature.nature_earth import get_natural_earth
from qkun.feature import (
        contains_part,
        contains_none,
        contains_full
        )

def get_collection(digests):
    results = []
    for digest_path in digests:
        with open(digest_path, "r") as f:
            digest = yaml.safe_load(f)
        results.append({
            "polygon" : Polygon(parse_polygon(digest["polygons"][0][0])),
            "basename" : get_basename(digest_path),
            "image" : find_image(get_basename(digest_path))
        })
    return results

def load_image(image_path):
    image = mpimg.imread(image_path)
    # mask out white (255,255,255), assumes image is RGB or RGBA
    if image.shape[2] == 3:  # RGB
        mask = np.all(image[:, :, :3] > 254, axis=-1)
        image = np.dstack((image, (~mask).astype(np.uint8) * 255))
    # Add alpha channel
    elif image.shape[2] == 4:  # RGBA
        pass  # assume alpha already handled
    return image

fig = plt.figure(figsize=(10, 8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()
ax.coastlines()
ax.gridlines(draw_labels=True)
ax.add_feature(cfeature.BORDERS, linestyle=':')

digests = find_all_digests("2025-03-26", "2025-03-27")
collection = get_collection(digests)
land = get_natural_earth("land")

results = list(filter(lambda x: contains_none(land, x["polygon"]), collection))
polygons = [x["polygon"] for x in results]

feature = ShapelyFeature(polygons, ccrs.PlateCarree(), facecolor='none',
                         edgecolor='blue', linewidth=1)
ax.add_feature(feature)

for result in results:
    lon_min, lat_min, lon_max, lat_max = result["polygon"].bounds
    extent = [lon_min, lon_max, lat_min, lat_max]

    if result["image"] is None:
        continue

    image = load_image(result["image"])
    #image = mpimg.imread(image_path)
    ax.imshow(image, origin='upper', extent=extent, 
            transform=ccrs.PlateCarree(), interpolation='bilinear')

#plt.legend()
plt.tight_layout()
plt.show()
