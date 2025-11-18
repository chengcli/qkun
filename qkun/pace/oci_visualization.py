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
    
    This function selects appropriate wavelength bands for RGB channels to create
    a natural-looking image where white surfaces (like clouds) appear white.
    - Red channel: red band closest to 650 nm
    - Green channel: blue band closest to 550 nm (from blue CCD)
    - Blue channel: blue band closest to 450 nm
    
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
    
    # Select appropriate bands for RGB channels for natural color
    # Red channel: wavelength closest to 650 nm
    red_idx = np.argmin(np.abs(red_wavelength - 650))
    red_channel = rhot_red[red_idx, :, :]
    
    # Green channel: wavelength closest to 550 nm (from blue CCD which goes up to 610 nm)
    green_idx = np.argmin(np.abs(blue_wavelength - 550))
    green_channel = rhot_blue[green_idx, :, :]
    
    # Blue channel: wavelength closest to 450 nm
    blue_idx = np.argmin(np.abs(blue_wavelength - 450))
    blue_channel = rhot_blue[blue_idx, :, :]
    
    # Stack to create RGB image
    rgb_image = np.ma.stack([red_channel, green_channel, blue_channel], axis=-1)
    
    # Apply contrast enhancement to make features visible
    if enhance_contrast:
        # Use histogram equalization approach for better visibility
        # Apply the same stretch to all channels to maintain color balance
        # First, get the overall intensity range
        all_data = []
        for i in range(3):
            channel = rgb_image[:, :, i]
            valid_data = channel.compressed()
            if len(valid_data) > 0:
                all_data.extend(valid_data)
        
        if len(all_data) > 0:
            # Use percentile-based stretch on combined data for consistent scaling
            vmin = np.percentile(all_data, 1)  # 1st percentile
            vmax = np.percentile(all_data, 99)  # 99th percentile
            
            # Apply the same stretch to all channels
            for i in range(3):
                channel = rgb_image[:, :, i]
                
                # Apply linear stretch
                stretched = (channel - vmin) / (vmax - vmin)
                stretched = np.ma.clip(stretched, 0, 1)
                
                # Apply gamma correction for additional enhancement (gamma < 1 brightens)
                gamma = 0.7  # Slightly less aggressive brightening to preserve colors
                stretched = np.ma.power(stretched, gamma)
                
                # Scale to 0-255 for 8-bit display
                rgb_image[:, :, i] = stretched * 255
        else:
            rgb_image[:, :, :] = 0
    else:
        # Simple percentile normalization with consistent scaling
        all_data = []
        for i in range(3):
            valid_data = rgb_image[:, :, i].compressed()
            if len(valid_data) > 0:
                all_data.extend(valid_data)
        
        if len(all_data) > 0:
            vmin = np.percentile(all_data, 2)
            vmax = np.percentile(all_data, 98)
            
            for i in range(3):
                channel = rgb_image[:, :, i]
                rgb_image[:, :, i] = np.ma.clip((channel - vmin) / (vmax - vmin), 0, 1) * 255
        else:
            rgb_image[:, :, :] = 0
    
    # Convert to uint8 for proper display
    rgb_image = rgb_image.astype(np.uint8)
    
    return rgb_image, lon, lat


def plot_false_color_image(nc_path: str, subsample: int = 5, 
                           ax: Optional[plt.Axes] = None,
                           save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot the false color image on a map projection with proper geographic coordinate mapping.
    
    Uses scatter plot to properly map each pixel to its actual lat/lon coordinates,
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
    
    ax.set_title('OCI False Color Image (Enhanced, Human Perception Weighted)', 
                 fontsize=14, fontweight='bold')
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"False color image saved to: {save_path}")
    
    return fig
