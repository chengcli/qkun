import os
import yaml
from .granule_handler import GranuleHandler

# --- Representer and Constructor ---

def represent_granule_handler(dumper, data):
    return dumper.represent_mapping("!GranuleHandler", data.__dict__)

def construct_granule_handler(loader, node):
    values = loader.construct_mapping(node)
    obj = GranuleHandler(
        name=values.get("instrument_name"),
        longname=values.get("instrument_longname"),
        verbose=values.get("verbose", False)
    )
    # Set optional fields
    for key in values:
        if hasattr(obj, key):
            setattr(obj, key, values[key])
    return obj

yaml.add_representer(GranuleHandler, represent_granule_handler)
yaml.add_constructor("!GranuleHandler", construct_granule_handler)

# --- Save and Load Interface ---

def save_to_yaml(obj: GranuleHandler, filepath: str):
    with open(filepath, 'w') as f:
        yaml.dump(obj, f, default_flow_style=False)

def load_from_yaml(filepath: str) -> GranuleHandler:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, 'r') as f:
        return yaml.load(f, Loader=yaml.Loader)

