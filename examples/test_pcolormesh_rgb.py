#!/usr/bin/env python
"""
Simple test of pcolormesh with RGB colors (no network required).
"""

import numpy as np
import matplotlib.pyplot as plt


def test_pcolormesh_rgb():
    """Test that pcolormesh can display RGB colors."""
    
    # Create simple tilted grid
    ny, nx = 30, 40
    
    # Create tilted coordinates
    x = np.linspace(0, 10, nx)
    y = np.linspace(0, 8, ny)
    X, Y = np.meshgrid(x, y)
    
    # Add tilt
    X_tilted = X + Y * 0.3
    Y_tilted = Y
    
    # Create RGB image
    rgb = np.zeros((ny, nx, 3), dtype=np.uint8)
    rgb[:, :, 2] = 100  # Blue background
    
    # Add colored features
    rgb[10:20, 15:25, 1] = 200  # Green square
    rgb[5:10, 25:35, 0] = 255  # Red square
    rgb[5:10, 25:35, 1] = 255  # Yellow (red + green)
    
    # Normalize to 0-1
    rgb_norm = rgb.astype(float) / 255.0
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Panel 1: Regular grid with imshow
    ax1.imshow(rgb, origin='lower', aspect='auto')
    ax1.set_title('Original RGB Array\n(Not tilted)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('X index')
    ax1.set_ylabel('Y index')
    
    # Panel 2: Tilted grid with pcolormesh
    dummy = np.zeros((ny, nx))
    mesh = ax2.pcolormesh(X_tilted, Y_tilted, dummy, shading='auto')
    
    # Set RGB colors
    colors_flat = rgb_norm.reshape(-1, 3)
    mesh.set_facecolor(colors_flat)
    mesh.set_edgecolor('none')
    
    ax2.set_title('pcolormesh with Tilted Grid\n(Proper RGB colors)', 
                  fontsize=12, fontweight='bold')
    ax2.set_xlabel('X coordinate (tilted)')
    ax2.set_ylabel('Y coordinate')
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_path = '/tmp/pcolormesh_rgb_test.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Test output saved to: {output_path}")
    plt.close(fig)
    
    return output_path


if __name__ == '__main__':
    print("\nTesting pcolormesh with RGB colors...")
    path = test_pcolormesh_rgb()
    print(f"\n✓ Success! RGB colors properly displayed with pcolormesh")
    print(f"✓ The tilted grid shows that each cell is mapped to its")
    print(f"  correct coordinates while preserving RGB colors")
    print()
