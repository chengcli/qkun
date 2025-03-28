import netCDF4
import yaml
import sys
from pathlib import Path

def parse_group_structure(group):
    """Parses a group and returns dimensions and variables metadata."""
    result = {}

    # Parse dimensions (only if non-empty)
    dimensions = {
        dim_name: (len(dim) if not dim.isunlimited() else "unlimited")
        for dim_name, dim in group.dimensions.items()
    }
    if dimensions:
        result['dimensions'] = dimensions

    # Parse variables
    variables = {}
    for var_name, var in group.variables.items():
        var_info = {
            'dimensions': list(var.dimensions),
            'attributes': {}
        }

        for attr_name in var.ncattrs():
            attr_value = getattr(var, attr_name)
            if isinstance(attr_value, bytes):
                attr_value = attr_value.decode('utf-8')
            elif hasattr(attr_value, 'tolist'):
                attr_value = attr_value.tolist()
            var_info['attributes'][attr_name] = attr_value

        variables[var_name] = var_info

    if variables:
        result['variables'] = variables

    # Recursively parse subgroups
    for subgrp_name, subgrp in group.groups.items():
        result[subgrp_name] = parse_group_structure(subgrp)

    return result

def save_to_yaml(data, output_yaml_path):
    """Writes data to a YAML file with proper formatting."""
    with open(output_yaml_path, 'w') as f:
        yaml.dump(data, f, sort_keys=False, default_flow_style=False)

def main(nc_file):
    nc_path = Path(nc_file)
    if not nc_path.exists():
        print(f"Error: NetCDF file '{nc_path}' does not exist.")
        sys.exit(1)

    dataset = netCDF4.Dataset(nc_path, mode='r')
    structure = {}

    for group_name, group in dataset.groups.items():
        structure[group_name] = parse_group_structure(group)

    dataset.close()

    yaml_path = nc_path.with_suffix('.vars.yaml')
    save_to_yaml(structure, yaml_path)
    print(f"YAML saved to: {yaml_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_nc_vars.py <input.nc>")
        sys.exit(1)

    main(sys.argv[1])

