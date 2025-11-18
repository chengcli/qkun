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
    Compute human perception weights at given wavelengths using three-Gaussian model.
    
    Models the three types of cone cells in human vision (S, M, L cones) which are
    sensitive to short (blue), medium (green), and long (red) wavelengths.
    Each cone type is approximated with a Gaussian distribution.
    
    Parameters:
    -----------
    wavelengths : np.ndarray
        Wavelengths in nanometers
        
    Returns:
    --------
    weights : np.ndarray
        Normalized human perception weights (sum to 1)
    """
    # Three-Gaussian model for human color perception
    # Based on the spectral sensitivity of S, M, L cone cells
    
    # S-cones (Short wavelength - Blue): peak ~445 nm
    blue_peak = 445.0  # nm
    blue_sigma = 40.0  # nm
    blue_response = np.exp(-0.5 * ((wavelengths - blue_peak) / blue_sigma) ** 2)
    
    # M-cones (Medium wavelength - Green): peak ~545 nm  
    green_peak = 545.0  # nm
    green_sigma = 50.0  # nm
    green_response = np.exp(-0.5 * ((wavelengths - green_peak) / green_sigma) ** 2)
    
    # L-cones (Long wavelength - Red): peak ~570 nm (but tail extends to 700+ nm)
    red_peak = 570.0  # nm
    red_sigma = 60.0  # nm (wider to capture red sensitivity)
    red_response = np.exp(-0.5 * ((wavelengths - red_peak) / red_sigma) ** 2)
    
    # Combine the three responses with appropriate weighting
    # Weight by relative contributions to luminosity perception
    weights = 0.3 * blue_response + 0.59 * green_response + 0.11 * red_response
    
    # Normalize weights to sum to 1
    if weights.sum() > 0:
        weights = weights / weights.sum()
    else:
        weights = np.ones_like(wavelengths) / len(wavelengths)
    
    return weights


def create_false_color_image(nc_path: str, subsample: int = 5, 
                            bright: float = 0.3) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Create an RGB image from OCI observation data following NASA VITALS recipe.
    
    This implementation follows the approach from NASA VITALS:
    https://nasa.github.io/VITALS/python/Exploring_PACE_OCI_L2_SFRFL.html
    
    Steps:
    1. Select bands nearest to Red (650nm), Green (560nm), Blue (470nm)
    2. Apply gamma adjustment based on mean of valid values
    3. Clip to [0, 1] range
    
    Parameters:
    -----------
    nc_path : str
        Path to the OCI netCDF file
    subsample : int, optional
        Subsampling factor for the data (default: 5)
    bright : float, optional
        Target brightness level for gamma adjustment (default: 0.3)
        Higher values = brighter image
        
    Returns:
    --------
    rgb_image : np.ndarray
        RGB image array with shape (scans, pixels, 3) scaled to 0-1 range
    lon : np.ndarray
        Longitude array (subsampled)
    lat : np.ndarray
        Latitude array (subsampled)
    """
    import math
    
    with Dataset(nc_path, 'r') as ds:
        # Get observation data
        obs_group = ds.groups['observation_data']
        rhot_blue = obs_group.variables['rhot_blue'][:, ::subsample, ::subsample]
        rhot_red = obs_group.variables['rhot_red'][:, ::subsample, ::subsample]
        
        # Get wavelengths
        params = ds.groups['sensor_band_parameters']
        blue_wavelength = params.variables['blue_wavelength'][:]
        red_wavelength = params.variables['red_wavelength'][:]
        
        # Get geolocation
        geo_group = ds.groups['geolocation_data']
        lon = geo_group.variables['longitude'][::subsample, ::subsample]
        lat = geo_group.variables['latitude'][::subsample, ::subsample]
    
    # Combine all wavelengths and data
    all_wavelengths = np.concatenate([blue_wavelength, red_wavelength])
    all_rhot = np.ma.concatenate([rhot_blue, rhot_red], axis=0)
    
    # Select bands nearest to target wavelengths (NASA VITALS approach)
    # Red: 650nm, Green: 560nm, Blue: 470nm
    target_wavelengths = [650, 560, 470]
    selected_bands = []
    
    for target_wl in target_wavelengths:
        # Find the band closest to the target wavelength
        idx = np.argmin(np.abs(all_wavelengths - target_wl))
        selected_bands.append(idx)
    
    # Extract the selected bands for RGB
    # Shape: (3, scans, pixels) -> (scans, pixels, 3)
    rgb_image = np.ma.stack([
        all_rhot[selected_bands[0], :, :],  # Red
        all_rhot[selected_bands[1], :, :],  # Green
        all_rhot[selected_bands[2], :, :]   # Blue
    ], axis=-1)
    
    # Apply gamma adjustment following NASA VITALS approach
    # Mask nan and negative values
    invalid = np.ma.getmaskarray(rgb_image) | (rgb_image.data < 0)
    valid = ~invalid
    
    # Calculate gamma based on the mean of valid values across all channels
    if np.any(valid):
        mean_valid = np.nanmean(rgb_image.data[valid])
        if mean_valid > 0:
            gamma = math.log(bright) / math.log(mean_valid)
        else:
            gamma = 1.0
    else:
        gamma = 1.0
    
    # Apply gamma correction and clip to [0, 1]
    scaled = np.full_like(rgb_image.data, np.nan)
    scaled[valid] = np.power(rgb_image.data[valid], gamma)
    rgb_image = np.ma.masked_invalid(np.clip(scaled, 0, 1))
    
    return rgb_image, lon, lat


def plot_false_color_image(nc_path: str, subsample: int = 5, bright: float = 0.3,
                           ax: Optional[plt.Axes] = None,
                           save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot the false color image on a map projection following NASA VITALS recipe.
    
    Uses scatter plot to properly map each pixel to its actual lat/lon coordinates,
    preserving the tilted satellite swath geometry and displaying true RGB colors.
    
    Follows the approach from NASA VITALS:
    https://nasa.github.io/VITALS/python/Exploring_PACE_OCI_L2_SFRFL.html
    
    Parameters:
    -----------
    nc_path : str
        Path to the OCI netCDF file
    subsample : int, optional
        Subsampling factor for the data (default: 5)
    bright : float, optional
        Target brightness for gamma adjustment (default: 0.3)
        Higher values = brighter image
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If None, creates a new figure with cartopy projection
    save_path : str, optional
        Path to save the figure
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The figure object
    """
    # Create false color image using NASA VITALS approach
    rgb_image, lon, lat = create_false_color_image(nc_path, subsample, bright=bright)
    
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
    # RGB image is already in 0-1 range from gamma adjustment
    rgb_display = np.ma.filled(rgb_image, 0)
    
    # RGB is already normalized to 0-1 range
    rgb_normalized = rgb_display.astype(float)
    
    # For satellite swaths with tilted/irregular grids and RGB colors,
    # use scatter plot with square markers
    # This properly maps each pixel to its geographic location while displaying RGB colors
    
    # Flatten arrays
    ny, nx = rgb_normalized.shape[:2]
    lon_flat = lon.flatten()
    lat_flat = lat.flatten()
    colors_flat = rgb_normalized.reshape(-1, 3)
    
    # Calculate appropriate marker size for coverage
    # Estimate pixel spacing
    if ny > 1 and nx > 1:
        # Calculate average spacing in degrees
        lon_spacing = np.abs(np.diff(lon, axis=1)).mean() if nx > 1 else 0.1
        lat_spacing = np.abs(np.diff(lat, axis=0)).mean() if ny > 1 else 0.1
        avg_spacing = (lon_spacing + lat_spacing) / 2
        
        # Convert spacing to points for scatter marker size
        # This is approximate and may need adjustment
        # Get axis size in points
        bbox = ax.get_window_extent()
        ax_width_pts = bbox.width
        ax_height_pts = bbox.height
        
        # Get data range
        lon_range = lon.max() - lon.min()
        lat_range = lat.max() - lat.min()
        
        # Calculate points per degree (approximate)
        pts_per_deg_lon = ax_width_pts / lon_range if lon_range > 0 else 100
        pts_per_deg_lat = ax_height_pts / lat_range if lat_range > 0 else 100
        pts_per_deg = (pts_per_deg_lon + pts_per_deg_lat) / 2
        
        # Marker size in points^2 (add overlap factor)
        marker_size = (avg_spacing * pts_per_deg * 1.2) ** 2
        
        # Clamp to reasonable range
        marker_size = np.clip(marker_size, 1, 10000)
    else:
        marker_size = 100
    
    # Plot using scatter with square markers and RGB colors
    scatter = ax.scatter(lon_flat, lat_flat, c=colors_flat, s=marker_size,
                        marker='s', edgecolors='none',
                        transform=ccrs.PlateCarree(), zorder=1)
    
    # Set extent with margin
    margin = 1
    ax.set_extent([lon.min() - margin, lon.max() + margin,
                   lat.min() - margin, lat.max() + margin],
                  crs=ccrs.PlateCarree())
    
    ax.set_title('OCI False Color Image (NASA VITALS Recipe)', 
                 fontsize=14, fontweight='bold')
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"False color image saved to: {save_path}")
    
    return fig
