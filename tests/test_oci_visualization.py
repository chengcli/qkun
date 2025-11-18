"""
Test module for OCI visualization functions.

These tests validate the OCI visualization module functions without requiring actual NetCDF data.
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from qkun.pace.oci_visualization import (
    compute_human_perception_weights,
    plot_blue_spectrum,
    plot_red_spectrum,
    plot_observation_polygon,
    create_false_color_image,
    plot_false_color_image
)


class TestHumanPerceptionWeights(unittest.TestCase):
    """Test human perception weight computation."""
    
    def test_weights_normalized(self):
        """Test that weights sum to 1."""
        wavelengths = np.array([400, 450, 500, 550, 600, 650, 700])
        weights = compute_human_perception_weights(wavelengths)
        self.assertAlmostEqual(weights.sum(), 1.0, places=6)
    
    def test_weights_peak_at_green(self):
        """Test that weights peak near 555 nm (green)."""
        wavelengths = np.arange(400, 700, 10)
        weights = compute_human_perception_weights(wavelengths)
        
        # Find the wavelength with maximum weight
        max_idx = np.argmax(weights)
        peak_wavelength = wavelengths[max_idx]
        
        # Should be close to 555 nm
        self.assertLess(abs(peak_wavelength - 555), 20)
    
    def test_weights_positive(self):
        """Test that all weights are positive."""
        wavelengths = np.array([400, 500, 600, 700])
        weights = compute_human_perception_weights(wavelengths)
        self.assertTrue(np.all(weights >= 0))
    
    def test_weights_shape(self):
        """Test that output shape matches input shape."""
        wavelengths = np.array([400, 450, 500, 550, 600])
        weights = compute_human_perception_weights(wavelengths)
        self.assertEqual(weights.shape, wavelengths.shape)


class TestVisualizationFunctions(unittest.TestCase):
    """Test visualization functions with mocked NetCDF data."""
    
    def setUp(self):
        """Set up mock data for tests."""
        self.mock_nc_path = "test_file.nc"
        
        # Create mock data
        self.blue_wavelength = np.array([400, 420, 440, 460, 480, 500])
        self.blue_irradiance = np.array([1800, 1900, 2000, 2050, 2000, 1900])
        self.red_wavelength = np.array([600, 620, 640, 660, 680, 700])
        self.red_irradiance = np.array([1600, 1650, 1700, 1650, 1600, 1550])
        self.geospatial_bounds = "POLYGON((26.56697 8.91377, 2.74375 3.85615, 7.03795 -19.31054, 31.87486 -14.13918, 26.56697 8.91377))"
        
        # Mock observation data
        self.rhot_blue = np.random.rand(6, 10, 10) * 0.3  # 6 bands, 10x10 pixels
        self.rhot_red = np.random.rand(6, 10, 10) * 0.3
        self.longitude = np.linspace(2.5, 32, 10)
        self.latitude = np.linspace(-20, 9, 10)
        self.lon_grid, self.lat_grid = np.meshgrid(self.longitude, self.latitude)
    
    @patch('qkun.pace.oci_visualization.Dataset')
    def test_plot_blue_spectrum_creates_figure(self, mock_dataset):
        """Test that plot_blue_spectrum creates a figure."""
        # Mock the Dataset
        mock_ds = MagicMock()
        mock_params = MagicMock()
        mock_params.variables = {
            'blue_wavelength': self.blue_wavelength,
            'blue_solar_irradiance': self.blue_irradiance
        }
        mock_ds.groups = {'sensor_band_parameters': mock_params}
        mock_ds.__enter__ = Mock(return_value=mock_ds)
        mock_ds.__exit__ = Mock(return_value=False)
        mock_dataset.return_value = mock_ds
        
        # Call the function
        fig = plot_blue_spectrum(self.mock_nc_path)
        
        # Verify figure was created
        self.assertIsInstance(fig, plt.Figure)
        plt.close(fig)
    
    @patch('qkun.pace.oci_visualization.Dataset')
    def test_plot_red_spectrum_creates_figure(self, mock_dataset):
        """Test that plot_red_spectrum creates a figure."""
        # Mock the Dataset
        mock_ds = MagicMock()
        mock_params = MagicMock()
        mock_params.variables = {
            'red_wavelength': self.red_wavelength,
            'red_solar_irradiance': self.red_irradiance
        }
        mock_ds.groups = {'sensor_band_parameters': mock_params}
        mock_ds.__enter__ = Mock(return_value=mock_ds)
        mock_ds.__exit__ = Mock(return_value=False)
        mock_dataset.return_value = mock_ds
        
        # Call the function
        fig = plot_red_spectrum(self.mock_nc_path)
        
        # Verify figure was created
        self.assertIsInstance(fig, plt.Figure)
        plt.close(fig)
    
    @patch('qkun.pace.oci_visualization.Dataset')
    def test_plot_observation_polygon_creates_map(self, mock_dataset):
        """Test that plot_observation_polygon creates a map figure."""
        # Mock the Dataset
        mock_ds = MagicMock()
        mock_ds.ncattrs.return_value = ['geospatial_bounds']
        mock_ds.getncattr.return_value = self.geospatial_bounds
        mock_ds.__enter__ = Mock(return_value=mock_ds)
        mock_ds.__exit__ = Mock(return_value=False)
        mock_dataset.return_value = mock_ds
        
        # Call the function
        fig = plot_observation_polygon(self.mock_nc_path)
        
        # Verify figure was created
        self.assertIsInstance(fig, plt.Figure)
        plt.close(fig)
    
    @patch('qkun.pace.oci_visualization.Dataset')
    def test_create_false_color_image_returns_correct_shapes(self, mock_dataset):
        """Test that create_false_color_image returns arrays with correct shapes."""
        # Mock the Dataset
        mock_ds = MagicMock()
        
        # Mock observation data group
        mock_obs = MagicMock()
        mock_obs.variables = {
            'rhot_blue': self.rhot_blue,
            'rhot_red': self.rhot_red
        }
        
        # Mock sensor band parameters group
        mock_params = MagicMock()
        mock_params.variables = {
            'blue_wavelength': self.blue_wavelength,
            'blue_solar_irradiance': self.blue_irradiance,
            'red_wavelength': self.red_wavelength,
            'red_solar_irradiance': self.red_irradiance
        }
        
        # Mock geolocation data group
        mock_geo = MagicMock()
        mock_geo.variables = {
            'longitude': self.lon_grid,
            'latitude': self.lat_grid
        }
        
        mock_ds.groups = {
            'observation_data': mock_obs,
            'sensor_band_parameters': mock_params,
            'geolocation_data': mock_geo
        }
        mock_ds.__enter__ = Mock(return_value=mock_ds)
        mock_ds.__exit__ = Mock(return_value=False)
        mock_dataset.return_value = mock_ds
        
        # Call the function
        rgb_image, lon, lat = create_false_color_image(self.mock_nc_path, subsample=1)
        
        # Verify shapes
        self.assertEqual(rgb_image.shape[2], 3)  # RGB channels
        self.assertEqual(lon.shape, lat.shape)  # Lon and lat same shape
        self.assertEqual(rgb_image.shape[0], lat.shape[0])  # Match spatial dimensions
        self.assertEqual(rgb_image.shape[1], lat.shape[1])


class TestPolygonParsing(unittest.TestCase):
    """Test parsing of geospatial_bounds POLYGON string."""
    
    @patch('qkun.pace.oci_visualization.Dataset')
    def test_polygon_parsing(self, mock_dataset):
        """Test that POLYGON string is correctly parsed."""
        bounds_str = "POLYGON((10.0 20.0, 15.0 25.0, 20.0 20.0, 10.0 20.0))"
        
        mock_ds = MagicMock()
        mock_ds.ncattrs.return_value = ['geospatial_bounds']
        mock_ds.getncattr.return_value = bounds_str
        mock_ds.__enter__ = Mock(return_value=mock_ds)
        mock_ds.__exit__ = Mock(return_value=False)
        mock_dataset.return_value = mock_ds
        
        # This should not raise an exception
        try:
            fig = plot_observation_polygon("test.nc")
            plt.close(fig)
            success = True
        except Exception as e:
            success = False
            print(f"Exception: {e}")
        
        self.assertTrue(success)


if __name__ == '__main__':
    # Run with minimal output for CI/CD
    unittest.main(verbosity=2)
