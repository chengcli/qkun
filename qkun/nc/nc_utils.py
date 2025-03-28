import netCDF4
import numpy as np

def open_dataset(nc_file):
    """Open a NetCDF file and return the Dataset object."""
    return netCDF4.Dataset(nc_file, mode='r')

def list_groups(dataset):
    """List all group names in the NetCDF dataset (top-level only)."""
    return list(dataset.groups.keys())

def list_variables(group):
    """List all variables in a given group."""
    return list(group.variables.keys())

def list_dimensions(group):
    """List dimensions and their sizes in the given group."""
    return {dim: len(group.dimensions[dim]) for dim in group.dimensions}

def get_variable_shape(group, var_name):
    """Get the shape of a variable."""
    return group.variables[var_name].shape

def get_variable_dtype(group, var_name):
    """Get the dtype of a variable."""
    return group.variables[var_name].dtype

def get_variable_attrs(group, var_name):
    """Get all attributes of a variable as a dictionary."""
    var = group.variables[var_name]
    return {attr: getattr(var, attr) for attr in var.ncattrs()}

def read_variable(group, var_name):
    """Read the full data array of a variable."""
    return group.variables[var_name][:]

def read_variable_slice(group, var_name, slices):
    """
    Read a slice of a variable.
    Example slices: (slice(0, 10), slice(None), 5)
    """
    return group.variables[var_name][slices]

def find_group(dataset, group_path):
    """
    Traverse a nested group path like 'group1/group2' to return the group object.
    """
    group = dataset
    for part in group_path.strip('/').split('/'):
        group = group.groups[part]
    return group

def close_dataset(dataset):
    """Close an opened NetCDF dataset."""
    dataset.close()

