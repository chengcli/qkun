import yaml
import os

def class_representer(dumper, data):
    return dumper.represent_mapping(f'!{data.__class__.__name__}', data.__dict__)

class GranuleHandler:
    DIGEST_SUFFIX = "global.yaml"
    FOOTPRINT_SUFFIX = "footprint.npz"

    def __init__(self, name, longname, verbose=False):
        self.name = name
        self.longname = longname
        self.verbose = verbose
        self.prefix = None
        self.basename = None

    def __repr__(self):
        result = f"Instrument({self.name}, {self.longname})"
        if self.prefix:
            result += f"\nPrefix: {self.prefix}"
        if self.basename:
            digest = f"{self.basename}.{self.DIGEST_SUFFIX}"
            result += f"\nDigest: {digest}, exists = {os.path.exists(self.digest_path())}"
            footprint = f"{self.basename}.{self.FOOTPRINT_SUFFIX}"
            result += f"\nFootprint: {footprint}, exists = {os.path.exists(self.footprint_path())}"
        return result
    
    def digest_path(self):
        return os.path.join(self.prefix, f"{self.basename}.{self.DIGEST_SUFFIX}")

    def footprint_path(self):
        return os.path.join(self.prefix, f"{self.basename}.{self.FOOTPRINT_SUFFIX}")

    def fov_path(self, alpha: float=0.0):
        return os.path.join(self.prefix, f"{self.basename}.fov_alpha={alpha:.2f}.txt")

    def process(self):
        raise NotImplementedError

    def get_fov(self, update_digest=True, cache=True):
        raise NotImplementedError

    def get_bounding_box(self, update_digest=True, cache=True):
        raise NotImplementedError

    def get_footprint(self, update_digest=True, cache=True):
        raise NotImplementedError

    def get_data(self, update_digest=True, cache=True):
        raise NotImplementedError
