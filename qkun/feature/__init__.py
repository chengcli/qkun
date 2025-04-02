from shapely.geometry import Polygon

def contains_part(feature, polygon: Polygon) -> bool:
    return polygon.intersects(feature) and not feature.contains(polygon)

def contains_full(feature, polygon: Polygon) -> bool:
    return feature.contains(polygon)

def contains_none(feature, polygon: Polygon) -> bool:
    return not polygon.intersects(feature) and not feature.contains(polygon)
