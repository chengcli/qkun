# OCI False Color Image Generator

This module provides functions to create false color images and various visualizations from OCI (Ocean Color Instrument) granule data.

## Features

1. **Spectral Plots**: Visualize solar irradiance across blue and red wavelength bands
2. **Map Projections**: Display observation regions with coastlines and geographic features
3. **Human Perception Weights**: Apply photopic luminosity function for realistic color perception
4. **False Color Images**: Generate human-perception weighted RGB images from multi-spectral data

## Installation

The module is part of the `qkun` package. All required dependencies are installed with the package.

## Usage

### Command Line

Use the provided script to process OCI netCDF files:

```bash
python examples/make_oci_false_color.py <path_to_oci_netcdf_file> [options]
```

Options:
- `--output-dir DIR`: Directory to save output plots (default: ./oci_output)
- `--subsample N`: Subsampling factor for false color image (default: 5)
- `--combined`: Create a combined figure with all plots

Example:
```bash
python examples/make_oci_false_color.py PACE_OCI.20250326T103301.L1B.nc \
    --output-dir ./output \
    --subsample 5 \
    --combined
```

### Python API

Import and use individual functions:

```python
from qkun.pace import (
    plot_blue_spectrum,
    plot_red_spectrum,
    plot_observation_polygon,
    plot_false_color_image,
    compute_human_perception_weights
)

# Plot individual spectra
fig1 = plot_blue_spectrum("path/to/file.nc", save_path="blue_spectrum.png")
fig2 = plot_red_spectrum("path/to/file.nc", save_path="red_spectrum.png")

# Plot observation region on map
fig3 = plot_observation_polygon("path/to/file.nc", save_path="region.png")

# Create false color image
fig4 = plot_false_color_image("path/to/file.nc", subsample=5, 
                               save_path="false_color.png")
```

## Implementation Details

### Step 1 & 2: Spectral Plots

The `plot_blue_spectrum()` and `plot_red_spectrum()` functions read the sensor band parameters from the netCDF file and plot the solar irradiance as a function of wavelength.

### Step 3: Map Projection

The `plot_observation_polygon()` function:
- Parses the `geospatial_bounds` POLYGON string from global attributes
- Creates a Cartopy map with PlateCarree projection
- Displays coastlines, borders, and geographic features
- Overlays the observation region polygon

### Step 4: Human Perception Weights

The `compute_human_perception_weights()` function implements a Gaussian approximation of the CIE 1924 photopic luminosity function:
- Peak sensitivity at 555 nm (green)
- Standard deviation of ~50 nm
- Normalized weights sum to 1

This simulates how the human eye perceives brightness at different wavelengths.

### Step 5: False Color Image

The `create_false_color_image()` function:
1. Loads blue and red band reflectance data (`rhot_blue`, `rhot_red`)
2. Computes human perception weights for each band's wavelengths
3. Weights each band by both human perception and solar irradiance
4. Creates RGB channels:
   - Red channel: weighted red bands
   - Green channel: average of weighted blue and red bands
   - Blue channel: weighted blue bands
5. Normalizes to 0-1 range using percentile clipping (2nd-98th percentile)

### Step 6: Combined Script

The `make_oci_false_color.py` script combines all steps into a single executable that:
- Validates input files
- Creates output directory
- Generates all plots (individual or combined)
- Saves outputs with descriptive filenames

## Data Requirements

The OCI netCDF file must contain:

### Global Attributes
- `geospatial_bounds`: POLYGON string with observation region coordinates

### Groups and Variables

**sensor_band_parameters:**
- `blue_wavelength`: Blue band wavelengths (nm)
- `blue_solar_irradiance`: Solar irradiance for blue bands (W m^-2 μm^-1)
- `red_wavelength`: Red band wavelengths (nm)
- `red_solar_irradiance`: Solar irradiance for red bands (W m^-2 μm^-1)

**observation_data:**
- `rhot_blue`: Top of atmosphere blue band reflectance (bands, scans, pixels)
- `rhot_red`: Top of atmosphere red band reflectance (bands, scans, pixels)

**geolocation_data:**
- `latitude`: Pixel latitudes (scans, pixels)
- `longitude`: Pixel longitudes (scans, pixels)

## Testing

Run the test suite:

```bash
python -m pytest tests/test_oci_visualization.py -v
```

The tests include:
- Human perception weight validation
- Spectrum plotting with mocked data
- Map projection rendering
- False color image generation
- POLYGON string parsing

## Output Files

When run with default settings, the script generates:

Individual mode:
- `{basename}_blue_spectrum.png`: Blue band solar irradiance plot
- `{basename}_red_spectrum.png`: Red band solar irradiance plot
- `{basename}_observation_polygon.png`: Map with observation region
- `{basename}_false_color.png`: Human-perception weighted false color image

Combined mode:
- `{basename}_combined.png`: Single figure with all plots

## Performance Notes

- Use the `--subsample` parameter to reduce processing time and file size
- Subsample factor of 5 (default) reduces data by 25x while maintaining visual quality
- Higher subsample values (10, 20) can be used for quick previews

## References

- CIE 1924 Photopic Luminosity Function
- PACE Mission: https://pace.gsfc.nasa.gov/
- OCI Instrument: Ocean Color Instrument specifications
