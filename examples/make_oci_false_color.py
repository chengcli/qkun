#!/usr/bin/env python
"""
OCI False Color Image Generator

This script processes OCI (Ocean Color Instrument) granule data to create
spectral plots, map projections, and false color images.

Usage:
    python make_oci_false_color.py <path_to_oci_netcdf_file> [--output-dir OUTPUT_DIR] [--subsample SUBSAMPLE]

Example:
    python make_oci_false_color.py PACE_OCI.20250326T103301.L1B.nc --output-dir ./output --subsample 5
"""

import os
import sys
import argparse
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from qkun.pace.oci_visualization import (
    plot_blue_spectrum,
    plot_red_spectrum,
    plot_observation_polygon,
    plot_false_color_image
)


def main():
    """Main function to generate all OCI visualizations."""
    parser = argparse.ArgumentParser(
        description='Generate false color images and plots from OCI granule data'
    )
    parser.add_argument('nc_file', type=str,
                       help='Path to the OCI netCDF file')
    parser.add_argument('--output-dir', type=str, default='./oci_output',
                       help='Directory to save output plots (default: ./oci_output)')
    parser.add_argument('--subsample', type=int, default=5,
                       help='Subsampling factor for false color image (default: 5)')
    parser.add_argument('--combined', action='store_true',
                       help='Create a combined figure with all plots')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.nc_file):
        print(f"Error: File not found: {args.nc_file}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Output directory: {args.output_dir}")
    
    # Get basename for output files
    basename = os.path.splitext(os.path.basename(args.nc_file))[0]
    
    print("\n" + "="*70)
    print("OCI FALSE COLOR IMAGE GENERATOR")
    print("="*70)
    print(f"Processing: {args.nc_file}")
    print(f"Basename: {basename}")
    print()
    
    if args.combined:
        # Create a combined figure with all plots
        print("Creating combined figure with all plots...")
        fig = plt.figure(figsize=(20, 12))
        
        # Step 1: Blue spectrum (top left)
        print("Step 1/5: Plotting blue solar irradiance spectrum...")
        ax1 = fig.add_subplot(2, 3, 1)
        plot_blue_spectrum(args.nc_file, ax=ax1)
        
        # Step 2: Red spectrum (top center)
        print("Step 2/5: Plotting red solar irradiance spectrum...")
        ax2 = fig.add_subplot(2, 3, 2)
        plot_red_spectrum(args.nc_file, ax=ax2)
        
        # Step 3: Observation polygon (top right)
        print("Step 3/5: Plotting observation polygon on map...")
        ax3 = fig.add_subplot(2, 3, 3, projection=ccrs.PlateCarree())
        plot_observation_polygon(args.nc_file, ax=ax3)
        
        # Step 4 & 5: False color image (bottom, spans all columns)
        print("Step 4/5: Computing human perception weights...")
        print("Step 5/5: Creating false color image...")
        ax4 = fig.add_subplot(2, 1, 2, projection=ccrs.PlateCarree())
        plot_false_color_image(args.nc_file, subsample=args.subsample, ax=ax4)
        
        plt.tight_layout()
        
        # Save combined figure
        output_path = os.path.join(args.output_dir, f"{basename}_combined.png")
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\nCombined figure saved to: {output_path}")
        
    else:
        # Create individual plots
        print("Step 1/5: Plotting blue solar irradiance spectrum...")
        fig1 = plot_blue_spectrum(
            args.nc_file,
            save_path=os.path.join(args.output_dir, f"{basename}_blue_spectrum.png")
        )
        plt.close(fig1)
        
        print("Step 2/5: Plotting red solar irradiance spectrum...")
        fig2 = plot_red_spectrum(
            args.nc_file,
            save_path=os.path.join(args.output_dir, f"{basename}_red_spectrum.png")
        )
        plt.close(fig2)
        
        print("Step 3/5: Plotting observation polygon on map...")
        fig3 = plot_observation_polygon(
            args.nc_file,
            save_path=os.path.join(args.output_dir, f"{basename}_observation_polygon.png")
        )
        plt.close(fig3)
        
        print("Step 4/5: Computing human perception weights...")
        print("Step 5/5: Creating false color image...")
        fig4 = plot_false_color_image(
            args.nc_file,
            subsample=args.subsample,
            save_path=os.path.join(args.output_dir, f"{basename}_false_color.png")
        )
        plt.close(fig4)
    
    print("\n" + "="*70)
    print("PROCESSING COMPLETE!")
    print("="*70)
    print(f"All plots saved to: {args.output_dir}")
    print()


if __name__ == '__main__':
    main()
