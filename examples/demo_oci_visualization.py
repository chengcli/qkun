#!/usr/bin/env python
"""
Demonstration script for OCI visualization module.

This script demonstrates how to use the OCI visualization functions
with mock data to show the API and expected behavior.
"""

import numpy as np
import matplotlib.pyplot as plt
from qkun.pace import compute_human_perception_weights


def demo_human_perception_weights():
    """Demonstrate the human perception weight calculation."""
    print("="*70)
    print("Demo: Human Perception Weights")
    print("="*70)
    
    # Generate wavelength range from 400 to 700 nm (visible spectrum)
    wavelengths = np.arange(400, 701, 10)
    
    # Compute human perception weights
    weights = compute_human_perception_weights(wavelengths)
    
    print(f"\nWavelength range: {wavelengths[0]} - {wavelengths[-1]} nm")
    print(f"Number of wavelengths: {len(wavelengths)}")
    print(f"Sum of weights: {weights.sum():.6f} (should be 1.0)")
    print(f"Peak weight at: {wavelengths[np.argmax(weights)]} nm (should be near 555 nm)")
    
    # Create a plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(wavelengths, weights, 'g-o', linewidth=2, markersize=6)
    ax.axvline(555, color='red', linestyle='--', label='Peak sensitivity (555 nm)')
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('Human Perception Weight', fontsize=12)
    ax.set_title('Photopic Luminosity Function (Human Eye Sensitivity)', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Save the plot
    output_file = '/tmp/human_perception_weights_demo.png'
    fig.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved to: {output_file}")
    plt.close(fig)
    
    # Show some sample weights
    print("\nSample weights:")
    print(f"  @ 450 nm (blue):   {weights[np.argmin(np.abs(wavelengths - 450))]:.4f}")
    print(f"  @ 555 nm (green):  {weights[np.argmin(np.abs(wavelengths - 555))]:.4f}")
    print(f"  @ 650 nm (red):    {weights[np.argmin(np.abs(wavelengths - 650))]:.4f}")
    print()


def demo_oci_band_weights():
    """Demonstrate weight calculation for typical OCI bands."""
    print("="*70)
    print("Demo: OCI Band Weights")
    print("="*70)
    
    # Typical OCI blue bands (approximate)
    blue_bands = np.array([340, 350, 360, 380, 400, 412, 445, 465, 490, 510, 555, 610])
    print(f"\nBlue band wavelengths: {blue_bands}")
    
    blue_weights = compute_human_perception_weights(blue_bands)
    print(f"Blue band weights: {blue_weights}")
    print(f"Sum: {blue_weights.sum():.6f}")
    
    # Typical OCI red bands (approximate)
    red_bands = np.array([620, 640, 655, 665, 673, 683, 710, 765, 865])
    print(f"\nRed band wavelengths: {red_bands}")
    
    red_weights = compute_human_perception_weights(red_bands)
    print(f"Red band weights: {red_weights}")
    print(f"Sum: {red_weights.sum():.6f}")
    
    # Create comparison plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    ax1.bar(range(len(blue_bands)), blue_weights, color='blue', alpha=0.7)
    ax1.set_xticks(range(len(blue_bands)))
    ax1.set_xticklabels([f'{w:.0f}' for w in blue_bands], rotation=45)
    ax1.set_xlabel('Wavelength (nm)', fontsize=11)
    ax1.set_ylabel('Weight', fontsize=11)
    ax1.set_title('Blue Band Weights', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    ax2.bar(range(len(red_bands)), red_weights, color='red', alpha=0.7)
    ax2.set_xticks(range(len(red_bands)))
    ax2.set_xticklabels([f'{w:.0f}' for w in red_bands], rotation=45)
    ax2.set_xlabel('Wavelength (nm)', fontsize=11)
    ax2.set_ylabel('Weight', fontsize=11)
    ax2.set_title('Red Band Weights', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    output_file = '/tmp/oci_band_weights_demo.png'
    fig.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved to: {output_file}")
    plt.close(fig)
    print()


def main():
    """Run all demonstrations."""
    print("\n" + "="*70)
    print("OCI VISUALIZATION MODULE DEMONSTRATION")
    print("="*70)
    print("\nThis script demonstrates the human perception weight calculation")
    print("used in the OCI false color image generation.\n")
    
    # Run demonstrations
    demo_human_perception_weights()
    demo_oci_band_weights()
    
    print("="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nGenerated files:")
    print("  - /tmp/human_perception_weights_demo.png")
    print("  - /tmp/oci_band_weights_demo.png")
    print("\nTo use with actual OCI data, run:")
    print("  python examples/make_oci_false_color.py <your_oci_file.nc>")
    print()


if __name__ == '__main__':
    main()
