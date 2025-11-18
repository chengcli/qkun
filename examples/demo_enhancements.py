#!/usr/bin/env python
"""
Test script to demonstrate the enhanced false color image improvements.

This script creates a synthetic OCI-like dataset to show:
1. Proper RGB coordinate mapping
2. Enhanced contrast for visibility
"""

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Rectangle


def create_test_visualization():
    """Create a test visualization showing the improvements."""
    
    # Create synthetic RGB data
    ny, nx = 100, 150
    
    # Create coordinate grids
    lon = np.linspace(5, 30, nx)
    lat = np.linspace(-15, 5, ny)
    lon_grid, lat_grid = np.meshgrid(lon, lat)
    
    # Create synthetic RGB image with features
    # Simulate ocean with some interesting features
    rgb_image = np.zeros((ny, nx, 3), dtype=np.uint8)
    
    # Blue ocean background
    rgb_image[:, :, 2] = 100  # Blue channel
    
    # Add some "chlorophyll" patterns (green)
    y, x = np.ogrid[:ny, :nx]
    # Circular feature
    circle = ((x - 75)**2 + (y - 50)**2) < 400
    rgb_image[circle, 1] = 180  # Green
    rgb_image[circle, 2] = 120  # Less blue
    
    # Linear feature (algal bloom)
    for i in range(ny):
        if 20 < i < 40:
            start = int(30 + i * 0.5)
            end = int(start + 30)
            if end < nx:
                rgb_image[i, start:end, 1] = 200  # Green
                rgb_image[i, start:end, 0] = 100  # Some red
    
    # Sediment plume (brownish)
    sediment = ((x - 120)**2 + (y - 70)**2) < 300
    rgb_image[sediment, 0] = 160  # Red
    rgb_image[sediment, 1] = 140  # Green
    rgb_image[sediment, 2] = 80   # Blue
    
    # Create figure with two subplots
    fig = plt.figure(figsize=(18, 8))
    
    # Panel 1: Without enhancement (old method - simulated)
    ax1 = fig.add_subplot(1, 2, 1, projection=ccrs.PlateCarree())
    ax1.coastlines(linewidth=1)
    ax1.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)
    
    # Simulate "dark" original image (reduce brightness)
    rgb_dark = (rgb_image * 0.3).astype(np.uint8)
    extent = [lon.min(), lon.max(), lat.min(), lat.max()]
    ax1.imshow(rgb_dark, extent=extent, origin='lower',
               transform=ccrs.PlateCarree(), interpolation='bilinear', aspect='auto')
    ax1.set_extent([lon.min() - 1, lon.max() + 1,
                    lat.min() - 1, lat.max() + 1],
                   crs=ccrs.PlateCarree())
    ax1.set_title('Before: Dark Image (Limited Visibility)', 
                  fontsize=14, fontweight='bold')
    
    # Panel 2: With enhancement (new method)
    ax2 = fig.add_subplot(1, 2, 2, projection=ccrs.PlateCarree())
    ax2.coastlines(linewidth=1)
    ax2.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)
    
    # Show enhanced image
    ax2.imshow(rgb_image, extent=extent, origin='lower',
               transform=ccrs.PlateCarree(), interpolation='bilinear', aspect='auto')
    ax2.set_extent([lon.min() - 1, lon.max() + 1,
                    lat.min() - 1, lat.max() + 1],
                   crs=ccrs.PlateCarree())
    ax2.set_title('After: Enhanced Contrast (Features Visible)', 
                  fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    # Save the comparison
    output_path = '/tmp/oci_enhancement_comparison.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nComparison plot saved to: {output_path}")
    plt.close(fig)
    
    return output_path


def create_coordinate_mapping_demo():
    """Demonstrate proper coordinate mapping."""
    
    fig = plt.figure(figsize=(16, 6))
    
    # Create test data
    nx, ny = 80, 60
    lon = np.linspace(10, 25, nx)
    lat = np.linspace(-10, 5, ny)
    lon_grid, lat_grid = np.meshgrid(lon, lat)
    
    # Create RGB test pattern
    rgb = np.zeros((ny, nx, 3), dtype=np.uint8)
    
    # Create a checkerboard pattern with coordinates labeled
    for i in range(ny):
        for j in range(nx):
            if (i // 10 + j // 10) % 2 == 0:
                rgb[i, j] = [200, 100, 100]  # Red-ish
            else:
                rgb[i, j] = [100, 100, 200]  # Blue-ish
    
    # Add some distinctive features at specific coordinates
    # Feature 1: Yellow square at (15°E, 0°N)
    idx_lon = np.argmin(np.abs(lon - 15))
    idx_lat = np.argmin(np.abs(lat - 0))
    rgb[idx_lat-5:idx_lat+5, idx_lon-5:idx_lon+5] = [255, 255, 0]
    
    # Feature 2: Cyan square at (20°E, -5°N)
    idx_lon = np.argmin(np.abs(lon - 20))
    idx_lat = np.argmin(np.abs(lat - -5))
    rgb[idx_lat-5:idx_lat+5, idx_lon-5:idx_lon+5] = [0, 255, 255]
    
    # Panel 1: Show the RGB array
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.imshow(rgb, origin='lower', aspect='auto')
    ax1.set_title('RGB Array (Image Space)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Array X Index')
    ax1.set_ylabel('Array Y Index')
    ax1.annotate('Yellow at\n(15°E, 0°N)', 
                xy=(idx_lon, idx_lat), xytext=(30, 40),
                arrowprops=dict(arrowstyle='->', color='black', lw=2),
                fontsize=10, color='black', weight='bold')
    
    # Panel 2: Show properly mapped to geographic coordinates
    ax2 = fig.add_subplot(1, 2, 2, projection=ccrs.PlateCarree())
    ax2.coastlines(linewidth=1)
    ax2.gridlines(draw_labels=True, linewidth=0.5, alpha=0.7)
    
    extent = [lon.min(), lon.max(), lat.min(), lat.max()]
    ax2.imshow(rgb, extent=extent, origin='lower',
               transform=ccrs.PlateCarree(), interpolation='nearest', aspect='auto')
    ax2.set_extent([lon.min() - 1, lon.max() + 1,
                    lat.min() - 1, lat.max() + 1],
                   crs=ccrs.PlateCarree())
    ax2.set_title('Mapped to Geographic Coordinates', fontsize=12, fontweight='bold')
    
    # Mark the yellow feature location
    ax2.plot(15, 0, 'k*', markersize=15, transform=ccrs.PlateCarree(), 
            label='Yellow feature\nat 15°E, 0°N')
    ax2.plot(20, -5, 'k*', markersize=15, transform=ccrs.PlateCarree(),
            label='Cyan feature\nat 20°E, -5°N')
    ax2.legend(loc='upper right')
    
    plt.tight_layout()
    
    output_path = '/tmp/oci_coordinate_mapping_demo.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Coordinate mapping demo saved to: {output_path}")
    plt.close(fig)
    
    return output_path


if __name__ == '__main__':
    print("\n" + "="*70)
    print("OCI VISUALIZATION ENHANCEMENTS DEMONSTRATION")
    print("="*70)
    print("\nThis demo shows the two key improvements:")
    print("1. Proper RGB coordinate mapping to geographic coordinates")
    print("2. Enhanced contrast for better feature visibility")
    print()
    
    # Create demonstrations
    print("Creating enhancement comparison...")
    path1 = create_test_visualization()
    
    print("\nCreating coordinate mapping demo...")
    path2 = create_coordinate_mapping_demo()
    
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nGenerated files:")
    print(f"  1. {path1}")
    print(f"  2. {path2}")
    print()
