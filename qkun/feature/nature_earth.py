import os
import pickle
from qkun import CACHE_FOLDER_PATH
from cartopy.io import shapereader
from shapely.ops import unary_union

def get_natural_earth(name, resolution='110m', category='physical'):
    save_file = os.path.join(CACHE_FOLDER_PATH,
                             f"{name}_{category}_{resolution}.pkl")
    if os.path.exists(save_file):
        with open(save_file, "rb") as f:
            return pickle.load(f)
    else:
        shapefile = shapereader.natural_earth(
                resolution=resolution,
                category=category,
                name=name)
        reader = shapereader.Reader(shapefile)
        feature_shapes = [record.geometry for record in reader.records()]
        feature_union = unary_union(feature_shapes)
        with open(save_file, "wb") as f:
            pickle.dump(feature_union, f)
        return feature_union
