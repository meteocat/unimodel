"""Tests building a netcdf from an xarray.
"""
import pickle
import unittest

import xarray

from unimodel.io.exporters import export_to_netcdf


class TestExporters(unittest.TestCase):
    """Tests exporters from xarray to netcdf."""

    def test_export_to_netcdf(self):
        """Test export xarray to netcdf."""
        netcdf_file = 'tests/data/out/reproject_models.nc'

        with open('tests/data/list_arome_xarray.pkl', 'rb') as file:
            arome_xarrays = pickle.load(file)
        with open('tests/data/list_bolam_xarray.pkl', 'rb') as file:
            bolam_xarrays = pickle.load(file)

        models_arrays = [arome_xarrays, bolam_xarrays]
        export_to_netcdf(models_arrays, netcdf_file)

        netcdf_data = xarray.open_dataset(netcdf_file)

        self.assertEqual(netcdf_data.dims['x'], 620)
        self.assertEqual(netcdf_data.dims['y'], 417)
        self.assertEqual(netcdf_data.dims['valid_time'], 1)
        self.assertEqual(netcdf_data.dims['model'], 2)

        self.assertAlmostEqual(netcdf_data.rio.transform().a,
                               0.010642497622783)
        self.assertAlmostEqual(netcdf_data.rio.transform().b, 0.0)
        self.assertAlmostEqual(netcdf_data.rio.transform().c,
                               -1.621137007661705)
        self.assertAlmostEqual(netcdf_data.rio.transform().d, 0.0)
        self.assertAlmostEqual(netcdf_data.rio.transform().e,
                               -0.010642497622783)
        self.assertAlmostEqual(netcdf_data.rio.transform().f,
                               43.455589042260094)
