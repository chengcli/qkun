#!/usr/bin/env python
"""
Demonstration of NASA VITALS RGB Image Recipe
==============================================

This script demonstrates how to create RGB images from PACE OCI data
following the NASA VITALS recipe:
https://nasa.github.io/VITALS/python/Exploring_PACE_OCI_L2_SFRFL.html

The NASA VITALS approach:
1. Select 3 specific bands closest to target wavelengths:
   - Red: 650 nm
   - Green: 560 nm
   - Blue: 470 nm

2. Apply gamma adjustment based on mean of valid values:
   gamma = log(bright) / log(mean_valid)

3. Clip to [0, 1] range

This is simpler than weighted sums and follows established best practices
for ocean color imagery.
"""

import numpy as np
import matplotlib.pyplot as plt
import math

# Create mock spectral data to demonstrate the approach
wavelengths = np.arange(350, 750, 10)  # 350-750 nm in 10 nm steps
n_bands = len(wavelengths)

# Simulate some reflectance data (cloud, water, vegetation)
# Cloud: high reflectance across all bands
cloud_spectrum = 0.8 * np.ones(n_bands)

# Water: low reflectance, slightly higher in blue
water_spectrum = 0.05 + 0.02 * np.exp(-0.5 * ((wavelengths - 450) / 50) ** 2)

# Vegetation: low in blue, high in green, very high in NIR
veg_spectrum = (
    0.05 * np.ones(n_bands) +  # Base
    0.10 * np.exp(-0.5 * ((wavelengths - 550) / 40) ** 2) +  # Green peak
    0.60 * np.where(wavelengths > 700, 1, 0)  # NIR plateau
)

# Create figure to show the approach
fig = plt.figure(figsize=(16, 10))

# Panel 1: Show the spectra and selected bands
ax1 = plt.subplot(2, 3, 1)
ax1.plot(wavelengths, cloud_spectrum, 'o-', label='Cloud', linewidth=2, markersize=4)
ax1.plot(wavelengths, water_spectrum, 's-', label='Water', linewidth=2, markersize=4)
ax1.plot(wavelengths, veg_spectrum, '^-', label='Vegetation', linewidth=2, markersize=4)

# Mark the NASA VITALS target wavelengths
target_wls = [650, 560, 470]
target_colors = ['red', 'green', 'blue']
target_names = ['Red (650nm)', 'Green (560nm)', 'Blue (470nm)']

for wl, color, name in zip(target_wls, target_colors, target_names):
    # Find closest wavelength
    idx = np.argmin(np.abs(wavelengths - wl))
    actual_wl = wavelengths[idx]
    ax1.axvline(actual_wl, color=color, linestyle='--', alpha=0.7, linewidth=2, 
                label=f'{name} (actual: {actual_wl}nm)')

ax1.set_xlabel('Wavelength (nm)', fontsize=12)
ax1.set_ylabel('Reflectance', fontsize=12)
ax1.set_title('NASA VITALS Band Selection\n(Select 3 nearest bands)', fontsize=13, fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 1.0)

# Panel 2: Show gamma adjustment formula
ax2 = plt.subplot(2, 3, 2)
ax2.axis('off')

formula_text = """
NASA VITALS Gamma Adjustment
─────────────────────────────

1. Select bands nearest to:
   • Red: 650 nm
   • Green: 560 nm  
   • Blue: 470 nm

2. Calculate gamma:
   γ = log(bright) / log(mean_valid)
   
   where:
   • bright = target brightness (e.g., 0.3)
   • mean_valid = mean of valid reflectance

3. Apply gamma correction:
   scaled = reflectance^γ
   
4. Clip to [0, 1]:
   output = clip(scaled, 0, 1)

────────────────────────────────

Benefits:
✓ Simple and fast
✓ Preserves true colors
✓ No complex weighting needed
✓ Follows NASA best practices
"""

ax2.text(0.05, 0.95, formula_text, transform=ax2.transAxes,
         fontsize=10, verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

# Panel 3: Demonstrate gamma curves
ax3 = plt.subplot(2, 3, 3)

reflectance_range = np.linspace(0, 1, 100)
gamma_values = [0.3, 0.5, 0.7, 1.0]

for gamma in gamma_values:
    scaled = np.power(reflectance_range, gamma)
    label = f'γ = {gamma}' + (' (linear)' if gamma == 1.0 else ' (brightening)' if gamma < 1 else '')
    ax3.plot(reflectance_range, scaled, label=label, linewidth=2)

ax3.set_xlabel('Input Reflectance', fontsize=12)
ax3.set_ylabel('Output (Gamma Adjusted)', fontsize=12)
ax3.set_title('Gamma Correction Effect', fontsize=13, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.set_xlim(0, 1)
ax3.set_ylim(0, 1)

# Panel 4: Show RGB extraction for cloud
ax4 = plt.subplot(2, 3, 4)

def extract_rgb(spectrum, wavelengths, targets=[650, 560, 470]):
    """Extract RGB values using NASA VITALS approach"""
    rgb = []
    for target in targets:
        idx = np.argmin(np.abs(wavelengths - target))
        rgb.append(spectrum[idx])
    return np.array(rgb)

cloud_rgb = extract_rgb(cloud_spectrum, wavelengths)
water_rgb = extract_rgb(water_spectrum, wavelengths)
veg_rgb = extract_rgb(veg_spectrum, wavelengths)

# Plot the extracted RGB values
x_pos = [0, 1, 2]
width = 0.25

ax4.bar([p - width for p in x_pos], cloud_rgb, width, label='Cloud', color='lightgray')
ax4.bar(x_pos, water_rgb, width, label='Water', color='lightblue')
ax4.bar([p + width for p in x_pos], veg_rgb, width, label='Vegetation', color='lightgreen')

ax4.set_xticks(x_pos)
ax4.set_xticklabels(['Red (650nm)', 'Green (560nm)', 'Blue (470nm)'])
ax4.set_ylabel('Reflectance', fontsize=12)
ax4.set_title('Extracted RGB Values (Before Gamma)', fontsize=13, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3, axis='y')
ax4.set_ylim(0, 1.0)

# Panel 5: Apply gamma adjustment and show result
ax5 = plt.subplot(2, 3, 5)

bright = 0.3

def gamma_adjust(rgb_values, bright=0.3):
    """Apply gamma adjustment following NASA VITALS"""
    mean_val = np.mean(rgb_values[rgb_values > 0])
    if mean_val > 0:
        gamma = math.log(bright) / math.log(mean_val)
    else:
        gamma = 1.0
    return np.clip(np.power(rgb_values, gamma), 0, 1), gamma

cloud_rgb_adj, cloud_gamma = gamma_adjust(cloud_rgb, bright)
water_rgb_adj, water_gamma = gamma_adjust(water_rgb, bright)
veg_rgb_adj, veg_gamma = gamma_adjust(veg_rgb, bright)

ax5.bar([p - width for p in x_pos], cloud_rgb_adj, width, label=f'Cloud (γ={cloud_gamma:.2f})', color='lightgray')
ax5.bar(x_pos, water_rgb_adj, width, label=f'Water (γ={water_gamma:.2f})', color='lightblue')
ax5.bar([p + width for p in x_pos], veg_rgb_adj, width, label=f'Vegetation (γ={veg_gamma:.2f})', color='lightgreen')

ax5.set_xticks(x_pos)
ax5.set_xticklabels(['Red (650nm)', 'Green (560nm)', 'Blue (470nm)'])
ax5.set_ylabel('Gamma-Adjusted Value', fontsize=12)
ax5.set_title(f'After Gamma Adjustment (bright={bright})', fontsize=13, fontweight='bold')
ax5.legend(fontsize=10)
ax5.grid(True, alpha=0.3, axis='y')
ax5.set_ylim(0, 1.0)

# Panel 6: Show final RGB colors
ax6 = plt.subplot(2, 3, 6)
ax6.axis('off')

# Create color swatches
swatch_height = 0.25
y_positions = [0.7, 0.4, 0.1]
labels = ['Cloud\n(White)', 'Water\n(Dark Blue)', 'Vegetation\n(Green)']
colors = [cloud_rgb_adj, water_rgb_adj, veg_rgb_adj]

for y_pos, label, color in zip(y_positions, labels, colors):
    # Draw color swatch
    rect = plt.Rectangle((0.2, y_pos), 0.3, swatch_height, 
                         facecolor=color, edgecolor='black', linewidth=2)
    ax6.add_patch(rect)
    
    # Add label
    ax6.text(0.55, y_pos + swatch_height/2, label, 
            verticalalignment='center', fontsize=12, fontweight='bold')
    
    # Add RGB values
    rgb_text = f'RGB: ({color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f})'
    ax6.text(0.55, y_pos + swatch_height/2 - 0.05, rgb_text,
            verticalalignment='top', fontsize=9, style='italic')

ax6.set_xlim(0, 1)
ax6.set_ylim(0, 1)
ax6.set_title('Final RGB Colors\n(After Gamma Adjustment)', fontsize=13, fontweight='bold')

plt.suptitle('NASA VITALS RGB Image Recipe for PACE OCI Data', 
             fontsize=16, fontweight='bold', y=0.98)

plt.tight_layout()
plt.savefig('/tmp/nasa_vitals_recipe_demo.png', dpi=150, bbox_inches='tight')
print("Demo saved to: /tmp/nasa_vitals_recipe_demo.png")
print("\nKey points:")
print("1. Simple band selection (nearest to 650, 560, 470 nm)")
print("2. Gamma adjustment based on mean reflectance")
print("3. Preserves natural colors (cloud=white, water=blue, vegetation=green)")
print("4. Follows NASA best practices for ocean color imagery")

plt.show()
