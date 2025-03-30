import os

CACHE_FOLDER_PATH = os.path.join(os.path.expanduser("~"), ".cache", "qkun")
CACHE_FOLDER_SIZE = 5.0 # in GB

if not os.path.exists(CACHE_FOLDER_PATH):
    os.makedirs(CACHE_FOLDER_PATH)
