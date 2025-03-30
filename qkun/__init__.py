import os

from .geobox import (
        GeoBox,
        add_geobox,
        get_projection,
        plot_geobox
        )

CACHE_FOLDER_PATH = os.path.join(os.path.expanduser("~"), ".cache", "qkun")

if not os.path.exists(CACHE_FOLDER_PATH):
    os.makedirs(CACHE_FOLDER_PATH)
