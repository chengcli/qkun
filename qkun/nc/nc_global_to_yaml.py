import netCDF4
import yaml
import sys
import os
from pathlib import Path

def parse_nc_global_attributes(nc_file_path):
    """Parses global attributes from a NetCDF file."""
    dataset = netCDF4.Dataset(nc_file_path, mode='r')
    global_attrs = {}

    for attr_name in dataset.ncattrs():
        attr_value = getattr(dataset, attr_name)

        # Convert bytes to string
        if isinstance(attr_value, bytes):
            attr_value = attr_value.decode('utf-8')
        # Convert numpy types or arrays to native Python types
        elif hasattr(attr_value, 'tolist'):
            attr_value = attr_value.tolist()

        global_attrs[attr_name] = attr_value

    dataset.close()
    return global_attrs

def save_to_yaml(data, output_yaml_path):
    """Saves a dictionary to a YAML file with proper indentation."""
    with open(output_yaml_path, 'w') as f:
        yaml.dump(data, f, sort_keys=False, default_flow_style=False)
