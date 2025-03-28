import sys
import os
import numpy as np
from scipy.spatial import ConvexHull
from pyproj import Proj, Transformer
from shapely.geometry import MultiPoint, Polygon, LineString
from shapely.ops import polygonize, unary_union
from scipy.spatial import Delaunay

def alpha_shape_2d(points, alpha=0.05):
    """Compute the alpha shape (concave hull) of a set of 2D points."""
    if len(points) < 4:
        return MultiPoint(points).convex_hull

    tri = Delaunay(points)
    edges = set()
    for ia, ib, ic in tri.simplices:
        pa, pb, pc = points[ia], points[ib], points[ic]
        a = np.linalg.norm(pb - pa)
        b = np.linalg.norm(pc - pb)
        c = np.linalg.norm(pa - pc)
        s = (a + b + c) / 2.0
        area = max(s * (s - a) * (s - b) * (s - c), 0.0) ** 0.5
        circum_r = (a * b * c) / (4.0 * area) if area > 0 else np.inf
        if circum_r < 1.0 / alpha:
            edges.update({tuple(sorted((ia, ib))), tuple(sorted((ib, ic))), tuple(sorted((ic, ia)))})

    edge_lines = [LineString([points[i], points[j]]) for i, j in edges]
    mls = unary_union(edge_lines)
    poly = unary_union(polygonize(mls))
    return poly

def compute_alpha_envelope(npz_path, alpha=0.05, max_points=10000):
    """Compute an alpha shape envelope in local Cartesian coordinates centered at mean lat/lon."""
    data = np.load(npz_path)
    lat = data["latitude"]
    lon = data["longitude"]

    if isinstance(lat, np.ma.MaskedArray):
        lat_mask = ~lat.mask
    else:
        lat_mask = np.ones_like(lat, dtype=bool)

    if isinstance(lon, np.ma.MaskedArray):
        lon_mask = ~lon.mask
    else:
        lon_mask = np.ones_like(lon, dtype=bool)

    mask = lat_mask & lon_mask
    lat_valid = lat[mask]
    lon_valid = lon[mask]

    # Subsample for performance
    if len(lat_valid) > max_points:
        indices = np.random.choice(len(lat_valid), max_points, replace=False)
        lat_valid = lat_valid[indices]
        lon_valid = lon_valid[indices]

    # Compute center
    lat0 = np.mean(lat_valid)
    lon0 = np.mean(lon_valid)

    # Define Azimuthal Equidistant projection centered at (lat0, lon0)
    proj_aeqd = Proj(proj='aeqd', lat_0=lat0, lon_0=lon0, units='m')
    transformer_to_xy = Transformer.from_proj("epsg:4326", proj_aeqd, always_xy=True)
    transformer_to_latlon = Transformer.from_proj(proj_aeqd, "epsg:4326", always_xy=True)

    # Project to x-y plane
    x, y = transformer_to_xy.transform(lon_valid, lat_valid)
    points_xy = np.column_stack((x, y))

    # Compute alpha shape or convex hull
    if alpha == 0: # convex hull
        print("Computing convex hull...")
        poly = ConvexHull(points_xy)
        envelope_xy = points_xy[poly.vertices]
    else:   # alpha shape
        poly = alpha_shape_2d(points_xy, alpha=alpha)
        if isinstance(poly, Polygon):
            envelope_xy = np.array(poly.exterior.coords)
        elif hasattr(poly, 'geoms'):
            # Try to extract the largest polygon from the collection
            polygons = [g for g in poly.geoms if isinstance(g, Polygon)]
            if polygons:
                largest = max(polygons, key=lambda p: p.area)
                envelope_xy = np.array(largest.exterior.coords)
            else:
                # fallback: convex hull
                fallback = MultiPoint(points_xy).convex_hull
                envelope_xy = np.array(fallback.exterior.coords)
        else:
            # final fallback
            fallback = MultiPoint(points_xy).convex_hull
            envelope_xy = np.array(fallback.exterior.coords)

    # add the first one to the last to close the polygon
    envelope_xy = np.vstack((envelope_xy, envelope_xy[0]))

    # Convert envelope back to lon/lat
    lon_env, lat_env = transformer_to_latlon.transform(envelope_xy[:, 0], envelope_xy[:, 1])

    # output path
    basename = os.path.basename(npz_path)
    outname = f"{os.path.splitext(basename)[0]}_alpha={alpha:.2f}.txt"

    # Save to .txt file as: lon lat
    envelope_coords = np.column_stack((lon_env, lat_env))
    np.savetxt(outname, envelope_coords, fmt="%.6f", delimiter=" ")
    print(f"Envelope written to: {outname} (lon lat format)")
    return envelope_coords[:, 1], envelope_coords[:, 0]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python compute_alpha_envelope.py <latlon.npz>")
        sys.exit(1)
    compute_alpha_envelope(sys.argv[1], alpha = 0.)
