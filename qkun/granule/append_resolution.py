import yaml
import numpy as np

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance (in km) between two points on Earth."""
    R = 6371.0  # Earth radius in km
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (np.sin(dlat / 2)**2 +
         np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2)
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def append_resolution_to_yaml(lat, lon, yaml_file):
    """Compute pixel resolution from geolocation and append to YAML."""
    # Ensure masking is respected if present
    if isinstance(lat, np.ma.MaskedArray):
        lat_mask = ~lat.mask
    else:
        lat_mask = np.ones_like(lat, dtype=bool)

    if isinstance(lon, np.ma.MaskedArray):
        lon_mask = ~lon.mask
    else:
        lon_mask = np.ones_like(lon, dtype=bool)

    mask = lat_mask & lon_mask

    # Calculate distance between adjacent pixels along scan lines
    dists = []
    for i in range(lat.shape[0]):  # each scan line
        lat_line = lat[i]
        lon_line = lon[i]
        valid = mask[i]
        if np.sum(valid) < 2:
            continue
        lat_line = lat_line[valid]
        lon_line = lon_line[valid]
        d = haversine(lat_line[:-1], lon_line[:-1], lat_line[1:], lon_line[1:])
        dists.append(d)

    if not dists:
        raise ValueError("No valid pixel distances found.")

    all_dists = np.concatenate(dists)
    min_res = float(np.min(all_dists))
    max_res = float(np.max(all_dists))

    # Append to YAML
    with open(yaml_file, "r") as f:
        meta = yaml.safe_load(f)

    meta["spatial_resolution_min_km"] = round(min_res, 3)
    meta["spatial_resolution_max_km"] = round(max_res, 3)

    with open(yaml_file, "w") as f:
        yaml.dump(meta, f, sort_keys=False)

    print(f"Updated YAML with resolution: min={min_res:.3f} km, max={max_res:.3f} km")
