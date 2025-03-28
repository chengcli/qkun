import cartopy.crs as ccrs
import cartopy.feature as cfeature

class GeoBox:
    latmin: float
    latmax: float
    lonmin: float
    lonmax: float
    angle: float

    def __init__(self, latmin=0., latmax=0., lonmin=0., lonmax=0., angle=0.):
        self.latmin = latmin
        self.latmax = latmax
        self.lonmin = lonmin
        self.lonmax = lonmax
        self.angle = angle

def add_geobox(ax, box, crs):
    lats = [box.latmax, box.latmax, box.latmin, box.latmin, box.latmax]

    # Detect wrap-around
    if box.lonmax < box.lonmin:
        lons = [box.lonmin, box.lonmax + 360.,
                box.lonmax + 360., box.lonmin, box.lonmin]
    else:
        lons = [box.lonmin, box.lonmax, box.lonmax, box.lonmin, box.lonmin]

    ax.plot(lons, lats, color='red', linewidth=1.5,
            transform=ccrs.PlateCarree(), label='GeoBox')

def get_projection(box):
    is_north_polar = box.latmin > 55 and box.latmax > 80
    is_south_polar = box.latmax < -55 and box.latmin < -80

    if is_north_polar:
        print("Using North Polar projection")
        projection = ccrs.NorthPolarStereo()
        extent = GeoBox(lonmin=-180, lonmax=180, latmin=55, latmax=90)
    elif is_south_polar:
        print("Using South Polar projection")
        projection = ccrs.SouthPolarStereo()
        extent = GeoBox(lomin=-180, lonmax=180, latmin=-90, latmax=-55)
    else:
        print("Using standard PlateCarree projection")
        projection = ccrs.PlateCarree()
        extent = box

    return projection, extent

def plot_geobox(ax, box, extent=None):
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS)
    ax.gridlines(draw_labels=True)

    if extent is None:
        extent = box

    ax.set_extent([extent.lonmin, extent.lonmax, 
                   extent.latmin, extent.latmax], crs=ccrs.PlateCarree())
    add_geobox(ax, box, crs=ccrs.PlateCarree())
