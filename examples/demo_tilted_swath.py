#!/usr/bin/env python
"""
Demonstration of proper RGB coordinate mapping for tilted satellite swaths.

This script shows how pcolormesh properly maps each pixel to its actual
lat/lon coordinates, preserving the tilted satellite swath geometry.
"""

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def create_tilted_swath_demo():
    """
    Create a demonstration showing tilted satellite swath with RGB colors.
    """
    
    # Simulate a tilted satellite swath (like OCI)
    # The swath is tilted at an angle, not aligned with lat/lon grid
    
    ny, nx = 50, 80
    
    # Create tilted coordinates (satellite swath path)
    # Start point
    lon_start, lat_start = 5, -15
    # End point (tilted)
    lon_end, lat_end = 28, 8
    
    # Create swath coordinates
    t = np.linspace(0, 1, ny)
    lon_center = lon_start + (lon_end - lon_start) * t
    lat_center = lat_start + (lat_end - lat_start) * t
    
    # Add width to the swath
    width_lon = 3
    width_lat = 2
    
    lon = np.zeros((ny, nx))
    lat = np.zeros((ny, nx))
    
    for i in range(ny):
        # Create cross-track variation
        cross_track = np.linspace(-1, 1, nx)
        # Add slight curvature
        lon[i, :] = lon_center[i] + cross_track * width_lon * (1 + 0.2 * t[i])
        lat[i, :] = lat_center[i] + cross_track * width_lat * (1 - 0.1 * t[i])
    
    # Create RGB image with distinct features
    rgb_image = np.zeros((ny, nx, 3), dtype=np.uint8)
    
    # Blue ocean background
    rgb_image[:, :, 2] = 120
    
    # Add colored features that should appear tilted
    # Green stripe along the swath
    rgb_image[15:25, :, 1] = 200
    rgb_image[15:25, :, 2] = 100
    
    # Red feature on one side
    rgb_image[30:40, 10:30, 0] = 220
    rgb_image[30:40, 10:30, 1] = 100
    rgb_image[30:40, 10:30, 2] = 80
    
    # Yellow feature on the other side
    rgb_image[5:15, 50:70, 0] = 255
    rgb_image[5:15, 50:70, 1] = 255
    rgb_image[5:15, 50:70, 2] = 50
    
    # Create figure with comparison
    fig = plt.figure(figsize=(20, 8))
    
    # Panel 1: Wrong approach - imshow with extent (rectangular, not tilted)
    ax1 = fig.add_subplot(1, 2, 1, projection=ccrs.PlateCarree())
    ax1.coastlines(linewidth=1)
    ax1.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)
    
    extent = [lon.min(), lon.max(), lat.min(), lat.max()]
    ax1.imshow(rgb_image, extent=extent, origin='lower',
               transform=ccrs.PlateCarree(), interpolation='nearest', aspect='auto')
    
    # Overlay the actual swath boundary
    boundary_lon = np.concatenate([lon[0, :], lon[:, -1], lon[-1, ::-1], lon[::-1, 0]])
    boundary_lat = np.concatenate([lat[0, :], lat[:, -1], lat[-1, ::-1], lat[::-1, 0]])
    ax1.plot(boundary_lon, boundary_lat, 'r-', linewidth=3, 
             transform=ccrs.PlateCarree(), label='Actual swath boundary')
    
    ax1.set_extent([lon.min() - 2, lon.max() + 2,
                    lat.min() - 2, lat.max() + 2],
                   crs=ccrs.PlateCarree())
    ax1.set_title('WRONG: imshow with extent\n(Rectangular, ignores tilt)', 
                  fontsize=14, fontweight='bold', color='red')
    ax1.legend(loc='upper left')
    
    ax1.text(0.5, 0.05, 'Image is rectangular,\ndoes not match tilted swath!',
             transform=ax1.transAxes, fontsize=12, ha='center',
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8),
             color='red', weight='bold')
    
    # Panel 2: Correct approach - pcolormesh with actual coordinates
    ax2 = fig.add_subplot(1, 2, 2, projection=ccrs.PlateCarree())
    ax2.coastlines(linewidth=1)
    ax2.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)
    
    # Normalize RGB to 0-1
    rgb_normalized = rgb_image.astype(float) / 255.0
    
    # Create dummy field for pcolormesh
    dummy = np.zeros(rgb_normalized.shape[:2])
    
    # Plot with pcolormesh to get proper coordinate mapping
    mesh = ax2.pcolormesh(lon, lat, dummy,
                          transform=ccrs.PlateCarree(),
                          shading='auto',
                          zorder=1)
    
    # Set RGB facecolors directly
    # Flatten RGB colors for each cell
    colors_flat = rgb_normalized.reshape(-1, 3)
    mesh.set_facecolor(colors_flat)
    mesh.set_edgecolor('none')
    
    ax2.set_extent([lon.min() - 2, lon.max() + 2,
                    lat.min() - 2, lat.max() + 2],
                   crs=ccrs.PlateCarree())
    ax2.set_title('CORRECT: pcolormesh with lat/lon\n(Properly tilted RGB image)', 
                  fontsize=14, fontweight='bold', color='green')
    
    ax2.text(0.5, 0.05, '✓ Each pixel mapped to\ncorrect lat/lon coordinates!',
             transform=ax2.transAxes, fontsize=12, ha='center',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8),
             color='darkgreen', weight='bold')
    
    plt.tight_layout()
    
    output_path = '/tmp/oci_tilted_swath_demo.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nTilted swath demonstration saved to: {output_path}")
    plt.close(fig)
    
    return output_path


if __name__ == '__main__':
    print("\n" + "="*70)
    print("TILTED SATELLITE SWATH RGB MAPPING DEMONSTRATION")
    print("="*70)
    print("\nThis demo shows the difference between:")
    print("1. imshow with extent (WRONG) - assumes rectangular grid")
    print("2. pcolormesh with lat/lon (CORRECT) - respects actual coordinates")
    print()
    print("Satellite swaths are tilted because the satellite moves along")
    print("its orbit path, not aligned with latitude/longitude lines.")
    print()
    
    path = create_tilted_swath_demo()
    
    print("\n" + "="*70)
    print("KEY POINTS:")
    print("="*70)
    print("✓ pcolormesh uses actual lat/lon for each pixel")
    print("✓ Preserves the tilted geometry of satellite swaths")
    print("✓ RGB colors are properly displayed")
    print("✓ Features appear at their correct geographic locations")
    print()
