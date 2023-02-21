"""Test geotools module.
"""
import pickle
import unittest

import pyproj

from unimodel.utils.geotools import proj4_from_grib, reproject_xarray


class TestGeoTools(unittest.TestCase):
    """Test geotools module."""
    with open('tests/data/xarray_model.pkl', 'rb') as file:
        data = pickle.load(file)

    def test_proj4_from_grib(self):
        """Tests get proj4 string from grib data."""
        projparams = proj4_from_grib(self.data)
        crs_xarray = pyproj.crs.CRS.from_dict(projparams)

        self.assertEqual(projparams['proj'],'ob_tran')
        self.assertEqual(projparams['o_lat_p'],50.0)
        self.assertEqual(projparams['o_lon_p'],0.0)
        self.assertEqual(crs_xarray.to_json_dict()['base_crs']['datum']
                         ['ellipsoid']['name'], 'WGS 84')

    def test_reproject_xarray(self):
        """Tests reproject an xarray."""
        dest_proj='EPSG:4326'
        corner_ul = (-1.621137007661705, 43.4555890422600939)
        grid_shape = (620, 417)
        grid_res = (0.010642497622783, 0.010642497622783)
        grid_repr=reproject_xarray(self.data, dest_proj, grid_shape,
                                   corner_ul, grid_res)

        self.assertEqual(grid_repr.shape, (417, 620))

        self.assertEqual(grid_repr.rio.crs.data['init'], 'epsg:4326')

        self.assertAlmostEqual(grid_repr.rio.transform().a, 0.0106,3)
        self.assertAlmostEqual(grid_repr.rio.transform().c, -1.6211,3)
        self.assertAlmostEqual(grid_repr.rio.transform().e, -0.0106,3)
        self.assertAlmostEqual(grid_repr.rio.transform().f, 43.4555,3)
