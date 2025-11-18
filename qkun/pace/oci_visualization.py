"""
OCI Visualization Module

This module provides functions to visualize and process OCI (Ocean Color Instrument) data
from PACE satellite granules, including spectral plots, map projections, and false color images.
"""

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from shapely.geometry import Polygon
from netCDF4 import Dataset
from typing import Tuple, Optional


def plot_blue_spectrum(nc_path: str, ax: Optional[plt.Axes] = None, 
                       save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot blue_solar_irradiance against blue_wavelength from OCI netCDF file.
    
    Parameters:
    -----------
    nc_path : str
        Path to the OCI netCDF file
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If None, creates a new figure
    save_path : str, optional
        Path to save the figure
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The figure object
    """
    with Dataset(nc_path, 'r') as ds:
        if 'sensor_band_parameters' not in ds.groups:
            raise ValueError("Group 'sensor_band_parameters' not found in NetCDF file.")
        
        params = ds.groups['sensor_band_parameters']
        blue_wavelength = params.variables['blue_wavelength'][:]
        blue_irradiance = params.variables['blue_solar_irradiance'][:]
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        fig = ax.get_figure()
    
    ax.plot(blue_wavelength, blue_irradiance, 'b-o', linewidth=2, markersize=6)
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('Solar Irradiance (W m$^{-2}$ μm$^{-1}$)', fontsize=12)
    ax.set_title('Blue Band Solar Irradiance Spectrum', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Blue spectrum plot saved to: {save_path}")
    
    return fig


def plot_red_spectrum(nc_path: str, ax: Optional[plt.Axes] = None,
                      save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot red_solar_irradiance against red_wavelength from OCI netCDF file.
    
    Parameters:
    -----------
    nc_path : str
        Path to the OCI netCDF file
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If None, creates a new figure
    save_path : str, optional
        Path to save the figure
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The figure object
    """
    with Dataset(nc_path, 'r') as ds:
        if 'sensor_band_parameters' not in ds.groups:
            raise ValueError("Group 'sensor_band_parameters' not found in NetCDF file.")
        
        params = ds.groups['sensor_band_parameters']
        red_wavelength = params.variables['red_wavelength'][:]
        red_irradiance = params.variables['red_solar_irradiance'][:]
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        fig = ax.get_figure()
    
    ax.plot(red_wavelength, red_irradiance, 'r-o', linewidth=2, markersize=6)
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('Solar Irradiance (W m$^{-2}$ μm$^{-1}$)', fontsize=12)
    ax.set_title('Red Band Solar Irradiance Spectrum', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Red spectrum plot saved to: {save_path}")
    
    return fig


def plot_observation_polygon(nc_path: str, ax: Optional[plt.Axes] = None,
                             save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot the observed polygon region from geospatial_bounds on a map with coastlines.
    
    Parameters:
    -----------
    nc_path : str
        Path to the OCI netCDF file
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If None, creates a new figure with cartopy projection
    save_path : str, optional
        Path to save the figure
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The figure object
    """
    with Dataset(nc_path, 'r') as ds:
        if 'geospatial_bounds' not in ds.ncattrs():
            raise ValueError("Global attribute 'geospatial_bounds' not found in NetCDF file.")
        
        bounds_str = ds.getncattr('geospatial_bounds')
    
    # Parse the POLYGON string
    # Format: "POLYGON((lon1 lat1, lon2 lat2, ...))"
    coords_str = bounds_str.replace('POLYGON((', '').replace('))', '')
    coord_pairs = coords_str.split(', ')
    lons = []
    lats = []
    for pair in coord_pairs:
        lon, lat = pair.split()
        lons.append(float(lon))
        lats.append(float(lat))
    
    if ax is None:
        fig = plt.figure(figsize=(12, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
    else:
        fig = ax.get_figure()
    
    # Add map features
    ax.add_feature(cfeature.LAND, facecolor='lightgray', edgecolor='none')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.5)
    ax.add_feature(cfeature.COASTLINE, linewidth=1.5)
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)
    
    # Plot the polygon
    ax.plot(lons, lats, 'r-', linewidth=2, transform=ccrs.PlateCarree(), 
            label='Observation Region')
    ax.fill(lons, lats, color='red', alpha=0.2, transform=ccrs.PlateCarree())
    
    # Set extent based on the polygon bounds
    margin = 2  # degrees
    ax.set_extent([min(lons) - margin, max(lons) + margin,
                   min(lats) - margin, max(lats) + margin],
                  crs=ccrs.PlateCarree())
    
    ax.legend(loc='upper right')
    ax.set_title('OCI Observation Region', fontsize=14, fontweight='bold')
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Observation polygon plot saved to: {save_path}")
    
    return fig


def compute_human_perception_weights(wavelengths: np.ndarray) -> np.ndarray:
    """
    Compute human perception weights at given wavelengths based on photopic luminosity function.
    
    The photopic luminosity function (CIE 1924) describes the average spectral sensitivity
    of human visual perception of brightness under daylight conditions.
    
    Parameters:
    -----------
    wavelengths : np.ndarray
        Wavelengths in nanometers
        
    Returns:
    --------
    weights : np.ndarray
        Normalized human perception weights (sum to 1)
    """
    # Photopic luminosity function approximation using Gaussian
    # Peak at 555 nm (green), with standard deviation ~50 nm
    peak_wavelength = 555.0  # nm (peak sensitivity in green)
    sigma = 50.0  # nm (approximate width of sensitivity curve)
    
    # Gaussian approximation of luminosity function
    weights = np.exp(-0.5 * ((wavelengths - peak_wavelength) / sigma) ** 2)
    
    # Normalize weights to sum to 1
    if weights.sum() > 0:
        weights = weights / weights.sum()
    else:
        weights = np.ones_like(wavelengths) / len(wavelengths)
    
    return weights


def create_false_color_image(nc_path: str, subsample: int = 5, 
                            enhance_contrast: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Create a human-perceived false color image from OCI observation data.
    
    This function applies human perception weights to the blue and red bands,
    normalizes by solar irradiance, and creates an RGB image where:
    - Red channel: weighted red bands
    - Green channel: average of weighted blue and red
    - Blue channel: weighted blue bands
    
    Parameters:
    -----------
    nc_path : str
        Path to the OCI netCDF file
    subsample : int, optional
        Subsampling factor for the data (default: 5)
    enhance_contrast : bool, optional
        Apply histogram equalization for better visibility (default: True)
        
    Returns:
    --------
    rgb_image : np.ndarray
        RGB image array with shape (scans, pixels, 3) scaled to 0-255 uint8
    lon : np.ndarray
        Longitude array (subsampled)
    lat : np.ndarray
        Latitude array (subsampled)
    """
    with Dataset(nc_path, 'r') as ds:
        # Get observation data
        obs_group = ds.groups['observation_data']
        rhot_blue = obs_group.variables['rhot_blue'][:, ::subsample, ::subsample]
        rhot_red = obs_group.variables['rhot_red'][:, ::subsample, ::subsample]
        
        # Get wavelengths and solar irradiance
        params = ds.groups['sensor_band_parameters']
        blue_wavelength = params.variables['blue_wavelength'][:]
        blue_irradiance = params.variables['blue_solar_irradiance'][:]
        red_wavelength = params.variables['red_wavelength'][:]
        red_irradiance = params.variables['red_solar_irradiance'][:]
        
        # Get geolocation
        geo_group = ds.groups['geolocation_data']
        lon = geo_group.variables['longitude'][::subsample, ::subsample]
        lat = geo_group.variables['latitude'][::subsample, ::subsample]
    
    # Compute human perception weights
    blue_weights = compute_human_perception_weights(blue_wavelength)
    red_weights = compute_human_perception_weights(red_wavelength)
    
    # Apply weights and normalize by solar irradiance
    # Weight by both human perception and solar irradiance
    blue_weights_norm = blue_weights * blue_irradiance
    blue_weights_norm = blue_weights_norm / blue_weights_norm.sum()
    
    red_weights_norm = red_weights * red_irradiance
    red_weights_norm = red_weights_norm / red_weights_norm.sum()
    
    # Weighted sum over bands
    blue_channel = np.ma.sum(rhot_blue * blue_weights_norm[:, None, None], axis=0)
    red_channel = np.ma.sum(rhot_red * red_weights_norm[:, None, None], axis=0)
    
    # Create green channel as average of blue and red for better visualization
    green_channel = (blue_channel + red_channel) / 2.0
    
    # Stack to create RGB image
    rgb_image = np.ma.stack([red_channel, green_channel, blue_channel], axis=-1)
    
    # Apply contrast enhancement to make features visible
    if enhance_contrast:
        # Use histogram equalization approach for better visibility
        for i in range(3):
            channel = rgb_image[:, :, i]
            # Get valid (non-masked) data
            valid_data = channel.compressed()
            
            if len(valid_data) > 0:
                # Use percentile-based stretch with aggressive clipping
                # This maps the useful range to full 0-255 dynamic range
                vmin = np.percentile(valid_data, 1)  # 1st percentile
                vmax = np.percentile(valid_data, 99)  # 99th percentile
                
                # Apply linear stretch
                stretched = (channel - vmin) / (vmax - vmin)
                stretched = np.ma.clip(stretched, 0, 1)
                
                # Apply gamma correction for additional enhancement (gamma < 1 brightens)
                gamma = 0.6  # Brightening factor
                stretched = np.ma.power(stretched, gamma)
                
                # Scale to 0-255 for 8-bit display
                rgb_image[:, :, i] = stretched * 255
            else:
                rgb_image[:, :, i] = 0
    else:
        # Simple percentile normalization
        for i in range(3):
            channel = rgb_image[:, :, i]
            vmin = np.percentile(channel.compressed(), 2)
            vmax = np.percentile(channel.compressed(), 98)
            rgb_image[:, :, i] = np.ma.clip((channel - vmin) / (vmax - vmin), 0, 1) * 255
    
    # Convert to uint8 for proper display
    rgb_image = rgb_image.astype(np.uint8)
    
    return rgb_image, lon, lat


def plot_false_color_image(nc_path: str, subsample: int = 5, 
                           ax: Optional[plt.Axes] = None,
                           save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot the false color image on a map projection with proper geographic coordinate mapping.
    
    Uses pcolormesh to properly map each pixel to its actual lat/lon coordinates,
    preserving the tilted satellite swath geometry and displaying true RGB colors.
    
    Parameters:
    -----------
    nc_path : str
        Path to the OCI netCDF file
    subsample : int, optional
        Subsampling factor for the data (default: 5)
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If None, creates a new figure with cartopy projection
    save_path : str, optional
        Path to save the figure
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The figure object
    """
    # Create false color image with contrast enhancement
    rgb_image, lon, lat = create_false_color_image(nc_path, subsample, enhance_contrast=True)
    
    if ax is None:
        fig = plt.figure(figsize=(14, 10))
        ax = plt.axes(projection=ccrs.PlateCarree())
    else:
        fig = ax.get_figure()
    
    # Add map features (with lower zorder so they appear behind the data)
    ax.add_feature(cfeature.LAND, facecolor='tan', edgecolor='none', zorder=0)
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3, zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=1, zorder=2)
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5, alpha=0.5, zorder=2)
    ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5, zorder=3)
    
    # Convert masked array to regular array, filling masked values with 0
    rgb_display = np.ma.filled(rgb_image, 0)
    
    # Normalize RGB to 0-1 range for matplotlib
    rgb_normalized = rgb_display.astype(float) / 255.0
    
    # For satellite swaths with tilted/irregular grids, we use pcolormesh
    # pcolormesh requires a dummy scalar field, but we can set face colors directly
    
    # Create a dummy scalar field (all zeros)
    dummy = np.zeros(rgb_normalized.shape[:2])
    
    # Plot with pcolormesh to get proper coordinate mapping
    mesh = ax.pcolormesh(lon, lat, dummy,
                         transform=ccrs.PlateCarree(),
                         shading='auto',
                         zorder=1)
    
    # Now set the facecolors to our RGB values
    # pcolormesh creates quadrilaterals, so we need to flatten and set colors
    # Get the number of faces (cells)
    ny, nx = rgb_normalized.shape[:2]
    n_cells = (ny - 1) * (nx - 1) if rgb_normalized.shape[:2] == lon.shape else ny * nx
    
    # Flatten RGB colors for each cell
    # If shading='auto' or 'flat', we need (ny-1, nx-1) colors
    # If shading='gouraud', we need (ny, nx) colors
    # With 'auto' on quadrilateral mesh, it uses 'flat' style
    
    # For 'flat' shading, pcolormesh uses the average of corner values
    # But we want to set explicit colors per cell
    # So we'll use the center color for each cell
    
    # Reshape RGB to match the number of faces
    if lon.shape == rgb_normalized.shape[:2]:
        # Data and coordinates have same shape, use direct mapping
        colors_flat = rgb_normalized.reshape(-1, 3)
    else:
        # Adjust if needed
        colors_flat = rgb_normalized.reshape(-1, 3)
    
    # Set the face colors
    # Don't call set_array(None) as it causes issues with cartopy
    # Just set the facecolors directly
    mesh.set_facecolor(colors_flat)
    mesh.set_edgecolor('none')
    
    # Set extent with margin
    margin = 1
    ax.set_extent([lon.min() - margin, lon.max() + margin,
                   lat.min() - margin, lat.max() + margin],
                  crs=ccrs.PlateCarree())
    
    ax.set_title('OCI False Color Image (Enhanced, Human Perception Weighted)', 
                 fontsize=14, fontweight='bold')
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"False color image saved to: {save_path}")
    
    return fig
