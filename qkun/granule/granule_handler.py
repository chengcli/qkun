import os

class GranuleHandler:
    def __init__(self, name, longname, verbose=False):
        self.instrument_name = name
        self.instrument_longname = longname
        self.verbose = verbose
        self.prefix = None
        self.url_path = None
        self.digest_path = None
        self.footprint_path = None
        self.fov_path = None
        self.data_path = None

    def __repr__(self):
        result = f"Instrument({self.name}, {self.longname})"
        if self.prefix:
            result += f"\nPrefix: {self.prefix}"
        if self.url_path:
            result += f"\nData URL: {self.url_path}"
        if self.digest_path:
            result += f"\nDigest: {self.digest_path}"
        if self.footprint_path:
            result += f"\nFootprint: {self.footprint_path}"
        if self.fov_path:
            result += f"\nFOV: {self.fov_path}"
        if self.data_path:
            result += f"\nData: {self.data_path}"
        return result

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
