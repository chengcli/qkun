import os
import fnmatch
from typing import List

CACHE_FOLDER_PATH = os.path.join(os.path.expanduser("~"), ".cache", "qkun")
CACHE_FOLDER_SIZE = 5.0 # in GB

CACHE_IMAGE_PATH = os.path.join(CACHE_FOLDER_PATH, "images")
CACHE_DIGEST_PATH = os.path.join(CACHE_FOLDER_PATH, "digests")

if not os.path.exists(CACHE_FOLDER_PATH):
    os.makedirs(CACHE_FOLDER_PATH)

if not os.path.exists(CACHE_IMAGE_PATH):
    os.makedirs(CACHE_IMAGE_PATH)

if not os.path.exists(CACHE_DIGEST_PATH):
    os.makedirs(CACHE_DIGEST_PATH)

def find_resource(pattern, search_path):
    for root, dirs, files in os.walk(search_path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                return os.path.join(root, name)
    return None

def find_digest(basename, search_dir=CACHE_DIGEST_PATH):
    return find_resource(f"{basename}.yaml", search_dir)

def find_all_digests(start_date: str, end_date: str,
                     collection=None) -> List[str]:
    folder = os.path.join(CACHE_DIGEST_PATH, f'{start_date},{end_date}')
    if not os.path.exists(folder):
        return []

    # if collection is None, loops through all collections
    if collection is None:
        result = []
        for root, dirs, files in os.walk(folder):
            result.extend([os.path.join(root, f) for f in files])
        return result
    else: # look for a specific collection
        return [os.path.join(folder, f) for f in os.listdir(folder)]

def get_basename(digest_path):
    return os.path.basename(digest_path).replace(".yaml", "")

def find_image(basename, search_dir=CACHE_IMAGE_PATH):
    return find_resource(f"{basename}.*.png", search_dir)
