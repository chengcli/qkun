import os

CACHE_FOLDER_PATH = os.path.join(os.path.expanduser("~"), ".cache", "qkun")
CACHE_FOLDER_SIZE = 5.0 # in GB

CACHE_IMAGE_PATH = os.path.join(CACHE_FOLDER_PATH, "images")
CACHE_POLYGON_PATH = os.path.join(CACHE_FOLDER_PATH, "polygons")

if not os.path.exists(CACHE_FOLDER_PATH):
    os.makedirs(CACHE_FOLDER_PATH)

if not os.path.exists(CACHE_IMAGE_PATH):
    os.makedirs(CACHE_IMAGE_PATH)

if not os.path.exists(CACHE_POLYGON_PATH):
    os.makedirs(CACHE_POLYGON_PATH)
