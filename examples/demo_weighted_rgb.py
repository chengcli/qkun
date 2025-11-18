#!/usr/bin/env python
"""
Demonstration of weighted RGB channel computation.

Shows the difference between:
- OLD: Selecting three individual bands
- NEW: Applying human perception weights to ALL bands
"""

import numpy as np
import matplotlib.pyplot as plt


def old_approach_select_bands():
    """Old approach: select 3 individual bands."""
    # Simulate OCI wavelengths
    blue_wavelengths = np.linspace(350, 610, 30)  # Blue CCD
    red_wavelengths = np.linspace(595, 850, 20)   # Red CCD
    all_wavelengths = np.concatenate([blue_wavelengths, red_wavelengths])
    
    # Select closest to target wavelengths
    red_target, green_target, blue_target = 650, 550, 450
    
    red_idx = np.argmin(np.abs(all_wavelengths - red_target))
    green_idx = np.argmin(np.abs(all_wavelengths - green_target))
    blue_idx = np.argmin(np.abs(all_wavelengths - blue_target))
    
    # Show which bands are selected
    selection = np.zeros_like(all_wavelengths)
    selection[red_idx] = 3  # Red
    selection[green_idx] = 2  # Green
    selection[blue_idx] = 1  # Blue
    
    return all_wavelengths, selection


def new_approach_weighted_bands():
    """New approach: weight ALL bands for each RGB channel."""
    # Simulate OCI wavelengths
    blue_wavelengths = np.linspace(350, 610, 30)
    red_wavelengths = np.linspace(595, 850, 20)
    all_wavelengths = np.concatenate([blue_wavelengths, red_wavelengths])
    
    # Simulate solar irradiance (peaks around 500nm, decreases toward UV and IR)
    solar_irradiance = 1800 * np.exp(-0.5 * ((all_wavelengths - 500) / 200) ** 2)
    
    # Compute human perception weights (three Gaussians)
    blue_peak, green_peak, red_peak = 445, 545, 570
    blue_sigma, green_sigma, red_sigma = 40, 50, 60
    
    s_cones = np.exp(-0.5 * ((all_wavelengths - blue_peak) / blue_sigma) ** 2)
    m_cones = np.exp(-0.5 * ((all_wavelengths - green_peak) / green_sigma) ** 2)
    l_cones = np.exp(-0.5 * ((all_wavelengths - red_peak) / red_sigma) ** 2)
    
    human_weights = 0.3 * s_cones + 0.59 * m_cones + 0.11 * l_cones
    human_weights = human_weights / human_weights.sum()
    
    # Compute RGB channel weights
    sigma_rgb = 40.0
    
    # Red channel: Gaussian at 650nm * human perception * solar irradiance
    red_gaussian = np.exp(-0.5 * ((all_wavelengths - 650) / sigma_rgb) ** 2)
    red_weights = red_gaussian * human_weights * solar_irradiance
    red_weights = red_weights / red_weights.sum()
    
    # Green channel: Gaussian at 545nm * human perception * solar irradiance
    green_gaussian = np.exp(-0.5 * ((all_wavelengths - 545) / sigma_rgb) ** 2)
    green_weights = green_gaussian * human_weights * solar_irradiance
    green_weights = green_weights / green_weights.sum()
    
    # Blue channel: Gaussian at 445nm * human perception * solar irradiance
    blue_gaussian = np.exp(-0.5 * ((all_wavelengths - 445) / sigma_rgb) ** 2)
    blue_weights = blue_gaussian * human_weights * solar_irradiance
    blue_weights = blue_weights / blue_weights.sum()
    
    return all_wavelengths, red_weights, green_weights, blue_weights, human_weights, solar_irradiance


def create_comparison():
    """Create comparison visualization."""
    
    # Get data from both approaches
    wl_old, selection = old_approach_select_bands()
    wl_new, red_w, green_w, blue_w, human_w, solar = new_approach_weighted_bands()
    
    fig = plt.figure(figsize=(16, 12))
    
    # Panel 1: Old approach - band selection
    ax1 = fig.add_subplot(3, 2, 1)
    colors_map = {0: 'gray', 1: 'blue', 2: 'green', 3: 'red'}
    for i, wl in enumerate(wl_old):
        color = colors_map[selection[i]]
        alpha = 1.0 if selection[i] > 0 else 0.3
        ax1.axvline(wl, color=color, alpha=alpha, linewidth=2 if selection[i] > 0 else 1)
    
    ax1.set_xlabel('Wavelength (nm)', fontsize=11)
    ax1.set_ylabel('Selected Bands', fontsize=11)
    ax1.set_title('OLD Approach: Select 3 Individual Bands\n(Only 3 bands used, rest ignored)', 
                  fontsize=12, fontweight='bold', color='red')
    ax1.set_xlim(350, 850)
    ax1.text(0.5, 0.5, '❌ Ignores most spectral information\n❌ No weighting by human perception\n❌ No weighting by solar irradiance',
             transform=ax1.transAxes, fontsize=10, ha='center', va='center',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # Panel 2: New approach - human perception weights
    ax2 = fig.add_subplot(3, 2, 2)
    ax2.fill_between(wl_new, 0, human_w, alpha=0.3, color='purple')
    ax2.plot(wl_new, human_w, 'purple', linewidth=2, label='Human Perception Weights')
    ax2.axvline(445, color='blue', linestyle='--', alpha=0.5, label='S-cones (445nm)')
    ax2.axvline(545, color='green', linestyle='--', alpha=0.5, label='M-cones (545nm)')
    ax2.axvline(570, color='red', linestyle='--', alpha=0.5, label='L-cones (570nm)')
    ax2.set_xlabel('Wavelength (nm)', fontsize=11)
    ax2.set_ylabel('Weight', fontsize=11)
    ax2.set_title('NEW Approach: Human Perception Weights\n(Three-Gaussian model: S, M, L cones)', 
                  fontsize=12, fontweight='bold', color='green')
    ax2.legend(loc='upper right', fontsize=9)
    ax2.set_xlim(350, 850)
    ax2.grid(True, alpha=0.3)
    
    # Panel 3: Solar irradiance
    ax3 = fig.add_subplot(3, 2, 3)
    ax3.fill_between(wl_new, 0, solar, alpha=0.3, color='orange')
    ax3.plot(wl_new, solar, 'orange', linewidth=2, label='Solar Irradiance')
    ax3.set_xlabel('Wavelength (nm)', fontsize=11)
    ax3.set_ylabel('Irradiance (W m⁻² μm⁻¹)', fontsize=11)
    ax3.set_title('Solar Irradiance Weighting\n(Extraterrestrial solar spectrum)', 
                  fontsize=12, fontweight='bold')
    ax3.legend(loc='upper right', fontsize=9)
    ax3.set_xlim(350, 850)
    ax3.grid(True, alpha=0.3)
    
    # Panel 4: Red channel weights
    ax4 = fig.add_subplot(3, 2, 4)
    ax4.fill_between(wl_new, 0, red_w, alpha=0.3, color='red')
    ax4.plot(wl_new, red_w, 'r-', linewidth=2, label='Red Channel Weights')
    ax4.axvline(650, color='red', linestyle='--', alpha=0.7, label='Target: 650nm')
    ax4.set_xlabel('Wavelength (nm)', fontsize=11)
    ax4.set_ylabel('Weight', fontsize=11)
    ax4.set_title('Red Channel = Gaussian(650nm) × Human × Solar\n(Weighted sum of ALL bands)', 
                  fontsize=12, fontweight='bold', color='darkred')
    ax4.legend(loc='upper right', fontsize=9)
    ax4.set_xlim(350, 850)
    ax4.grid(True, alpha=0.3)
    
    # Panel 5: Green channel weights
    ax5 = fig.add_subplot(3, 2, 5)
    ax5.fill_between(wl_new, 0, green_w, alpha=0.3, color='green')
    ax5.plot(wl_new, green_w, 'g-', linewidth=2, label='Green Channel Weights')
    ax5.axvline(545, color='green', linestyle='--', alpha=0.7, label='Target: 545nm')
    ax5.set_xlabel('Wavelength (nm)', fontsize=11)
    ax5.set_ylabel('Weight', fontsize=11)
    ax5.set_title('Green Channel = Gaussian(545nm) × Human × Solar\n(Weighted sum of ALL bands)', 
                  fontsize=12, fontweight='bold', color='darkgreen')
    ax5.legend(loc='upper right', fontsize=9)
    ax5.set_xlim(350, 850)
    ax5.grid(True, alpha=0.3)
    
    # Panel 6: Blue channel weights
    ax6 = fig.add_subplot(3, 2, 6)
    ax6.fill_between(wl_new, 0, blue_w, alpha=0.3, color='blue')
    ax6.plot(wl_new, blue_w, 'b-', linewidth=2, label='Blue Channel Weights')
    ax6.axvline(445, color='blue', linestyle='--', alpha=0.7, label='Target: 445nm')
    ax6.set_xlabel('Wavelength (nm)', fontsize=11)
    ax6.set_ylabel('Weight', fontsize=11)
    ax6.set_title('Blue Channel = Gaussian(445nm) × Human × Solar\n(Weighted sum of ALL bands)', 
                  fontsize=12, fontweight='bold', color='darkblue')
    ax6.legend(loc='upper right', fontsize=9)
    ax6.set_xlim(350, 850)
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_path = '/tmp/weighted_rgb_comparison.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nComparison saved to: {output_path}")
    plt.close(fig)
    
    return output_path


if __name__ == '__main__':
    print("\n" + "="*70)
    print("WEIGHTED RGB CHANNEL COMPUTATION")
    print("="*70)
    print("\nOLD Approach (WRONG):")
    print("  ❌ Select 3 individual bands (e.g., band closest to 450, 550, 650 nm)")
    print("  ❌ Ignores all other spectral information")
    print("  ❌ No human perception weighting")
    print("  ❌ No solar irradiance weighting")
    print()
    print("NEW Approach (CORRECT):")
    print("  ✓ Apply weights to ALL available bands")
    print("  ✓ Each RGB channel = weighted sum of all bands")
    print("  ✓ Weights = Gaussian(target) × Human Perception × Solar Irradiance")
    print("  ✓ Uses three-Gaussian human perception model (S, M, L cones)")
    print("  ✓ Accounts for solar spectral distribution")
    print()
    print("RGB Channel Computation:")
    print("  Red   = Σ(weight_red[i]   × reflectance[i]) for all i")
    print("  Green = Σ(weight_green[i] × reflectance[i]) for all i")
    print("  Blue  = Σ(weight_blue[i]  × reflectance[i]) for all i")
    print()
    
    path = create_comparison()
    
    print("\n" + "="*70)
    print("BENEFITS OF NEW APPROACH:")
    print("="*70)
    print("✓ Uses full spectral information from all bands")
    print("✓ Properly models human color perception")
    print("✓ Accounts for solar irradiance differences across spectrum")
    print("✓ More accurate and natural-looking false color images")
    print("✓ Reduces noise by averaging across multiple bands")
    print()
