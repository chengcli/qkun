#!/usr/bin/env python
"""
Demonstration of three-Gaussian human perception weights.

Shows how the improved weight function uses three Gaussians centered
on blue, green, and red wavelengths to better model human color vision.
"""

import numpy as np
import matplotlib.pyplot as plt


def old_single_gaussian(wavelengths):
    """Old approach: single Gaussian centered on green."""
    peak = 555.0
    sigma = 50.0
    weights = np.exp(-0.5 * ((wavelengths - peak) / sigma) ** 2)
    return weights / weights.sum() if weights.sum() > 0 else weights


def new_three_gaussian(wavelengths):
    """New approach: three Gaussians for blue, green, red."""
    # S-cones (Blue)
    blue_peak = 445.0
    blue_sigma = 40.0
    blue_response = np.exp(-0.5 * ((wavelengths - blue_peak) / blue_sigma) ** 2)
    
    # M-cones (Green)
    green_peak = 545.0
    green_sigma = 50.0
    green_response = np.exp(-0.5 * ((wavelengths - green_peak) / green_sigma) ** 2)
    
    # L-cones (Red)
    red_peak = 570.0
    red_sigma = 60.0
    red_response = np.exp(-0.5 * ((wavelengths - red_peak) / red_sigma) ** 2)
    
    # Combine with luminosity weights
    weights = 0.3 * blue_response + 0.59 * green_response + 0.11 * red_response
    return weights / weights.sum() if weights.sum() > 0 else weights


def create_comparison():
    """Create comparison visualization."""
    
    # Create wavelength range covering UV to near-IR
    wavelengths = np.linspace(300, 750, 500)
    
    # Compute weights
    old_weights = old_single_gaussian(wavelengths)
    new_weights = new_three_gaussian(wavelengths)
    
    # Also compute individual components for the new approach
    blue_peak, blue_sigma = 445.0, 40.0
    green_peak, green_sigma = 545.0, 50.0
    red_peak, red_sigma = 570.0, 60.0
    
    blue_component = np.exp(-0.5 * ((wavelengths - blue_peak) / blue_sigma) ** 2)
    green_component = np.exp(-0.5 * ((wavelengths - green_peak) / green_sigma) ** 2)
    red_component = np.exp(-0.5 * ((wavelengths - red_peak) / red_sigma) ** 2)
    
    # Normalize components for visualization
    blue_component = blue_component / blue_component.max() * 0.3
    green_component = green_component / green_component.max() * 0.59
    red_component = red_component / red_component.max() * 0.11
    
    fig = plt.figure(figsize=(16, 10))
    
    # Panel 1: Old approach (single Gaussian)
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.fill_between(wavelengths, 0, old_weights, alpha=0.3, color='green')
    ax1.plot(wavelengths, old_weights, 'g-', linewidth=2, label='Single Gaussian (Green only)')
    ax1.axvline(555, color='green', linestyle='--', alpha=0.5, label='Peak at 555 nm')
    ax1.set_xlabel('Wavelength (nm)', fontsize=12)
    ax1.set_ylabel('Weight', fontsize=12)
    ax1.set_title('OLD Approach: Single Gaussian\n(Only green sensitivity)', 
                  fontsize=13, fontweight='bold', color='red')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(300, 750)
    
    # Panel 2: New approach (three Gaussians combined)
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.fill_between(wavelengths, 0, new_weights, alpha=0.3, color='purple')
    ax2.plot(wavelengths, new_weights, 'purple', linewidth=2, 
             label='Combined (Blue + Green + Red)')
    ax2.set_xlabel('Wavelength (nm)', fontsize=12)
    ax2.set_ylabel('Weight', fontsize=12)
    ax2.set_title('NEW Approach: Three Gaussians Combined\n(Models S, M, L cone cells)', 
                  fontsize=13, fontweight='bold', color='green')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(300, 750)
    
    # Panel 3: Individual components
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.fill_between(wavelengths, 0, blue_component, alpha=0.3, color='blue', label='S-cones (Blue)')
    ax3.plot(wavelengths, blue_component, 'b-', linewidth=2)
    ax3.fill_between(wavelengths, 0, green_component, alpha=0.3, color='green', label='M-cones (Green)')
    ax3.plot(wavelengths, green_component, 'g-', linewidth=2)
    ax3.fill_between(wavelengths, 0, red_component, alpha=0.3, color='red', label='L-cones (Red)')
    ax3.plot(wavelengths, red_component, 'r-', linewidth=2)
    
    ax3.axvline(445, color='blue', linestyle='--', alpha=0.5)
    ax3.axvline(545, color='green', linestyle='--', alpha=0.5)
    ax3.axvline(570, color='red', linestyle='--', alpha=0.5)
    
    ax3.set_xlabel('Wavelength (nm)', fontsize=12)
    ax3.set_ylabel('Relative Sensitivity', fontsize=12)
    ax3.set_title('Individual Cone Responses\n(Blue peak: 445nm, Green: 545nm, Red: 570nm)', 
                  fontsize=13, fontweight='bold')
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(300, 750)
    
    # Panel 4: Direct comparison
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.plot(wavelengths, old_weights, 'g--', linewidth=2, alpha=0.7, 
             label='OLD: Single Gaussian')
    ax4.plot(wavelengths, new_weights, 'purple', linewidth=2, 
             label='NEW: Three Gaussians')
    ax4.set_xlabel('Wavelength (nm)', fontsize=12)
    ax4.set_ylabel('Weight', fontsize=12)
    ax4.set_title('Direct Comparison\n(New approach captures RGB sensitivity)', 
                  fontsize=13, fontweight='bold')
    ax4.legend(loc='upper right', fontsize=11)
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(300, 750)
    
    # Add text box explaining improvements
    ax4.text(0.5, 0.15, 
             '✓ Blue sensitivity captured\n✓ Green sensitivity improved\n✓ Red sensitivity added\n✓ Better color balance',
             transform=ax4.transAxes, fontsize=11, ha='center',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8),
             weight='bold', color='darkgreen')
    
    plt.tight_layout()
    
    output_path = '/tmp/three_gaussian_comparison.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nComparison saved to: {output_path}")
    plt.close(fig)
    
    return output_path


if __name__ == '__main__':
    print("\n" + "="*70)
    print("THREE-GAUSSIAN HUMAN PERCEPTION WEIGHTS")
    print("="*70)
    print("\nImprovement: Use three Gaussians instead of one")
    print()
    print("OLD Approach:")
    print("  - Single Gaussian centered at 555 nm (green)")
    print("  - Only models luminosity, not color")
    print("  - Poor representation of RGB sensitivity")
    print()
    print("NEW Approach:")
    print("  - Three Gaussians modeling S, M, L cone cells")
    print("  - S-cones (Blue): peak at 445 nm")
    print("  - M-cones (Green): peak at 545 nm")
    print("  - L-cones (Red): peak at 570 nm")
    print("  - Combined with luminosity weights: 0.3B + 0.59G + 0.11R")
    print()
    
    path = create_comparison()
    
    print("\n" + "="*70)
    print("BENEFITS:")
    print("="*70)
    print("✓ Captures sensitivity to blue wavelengths")
    print("✓ Captures sensitivity to red wavelengths")
    print("✓ Better models human color vision")
    print("✓ Produces more natural-looking false color images")
    print()
