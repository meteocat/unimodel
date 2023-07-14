"""Tests downscaling interpolation module.
"""
import pickle
import unittest
from unimodel.downscaling.interpolation import (bilinear, nearest)


class TestInterpolation(unittest.TestCase):
    """Tests different interpolation methodologies"""
    with open('tests/data/xarray_model.pkl', 'rb') as file:
        data = pickle.load(file)

    def test_bilinear(self):
        """Tests bilinear interpolation with and without projection"""
        # Test without specifying any projection, assuming the output
        # projection is the same as input
        corner_ul = (-7.2375, -4.9875)
        grid_shape = (138, 194)
        grid_res = (0.0075, 0.0075)

        grid_repr = bilinear(self.data, corner_ul, grid_shape, grid_res)

        self.assertEqual(grid_repr.shape, (138, 194))

        self.assertEqual(grid_repr.rio.crs.data['proj'], 'ob_tran')
        self.assertEqual(grid_repr.rio.crs.data['o_proj'], 'longlat')
        self.assertEqual(grid_repr.rio.crs.data['o_lat_p'], 50)
        self.assertEqual(grid_repr.rio.crs.data['lon_0'], 358.5)

        self.assertAlmostEqual(grid_repr.rio.transform().a, 0.0075, 3)
        self.assertAlmostEqual(grid_repr.rio.transform().c, -7.2375, 3)
        self.assertAlmostEqual(grid_repr.rio.transform().e, -0.0075, 3)
        self.assertAlmostEqual(grid_repr.rio.transform().f, -4.9875, 3)

        # Test with a specified projection
        corner_ul = (-1.621137007661705, 43.4555890422600939)
        grid_shape = (620, 417)
        grid_res = (0.010642497622783, 0.010642497622783)
        grid_repr = bilinear(self.data, corner_ul, grid_shape, grid_res,
                             dest_proj='EPSG:4326')
        self.assertEqual(grid_repr.shape, (620, 417))

        self.assertEqual(grid_repr.rio.crs.data['init'], 'epsg:4326')

        self.assertAlmostEqual(grid_repr.rio.transform().a, 0.0106, 3)
        self.assertAlmostEqual(grid_repr.rio.transform().c, -1.6211, 3)
        self.assertAlmostEqual(grid_repr.rio.transform().e, -0.0106, 3)
        self.assertAlmostEqual(grid_repr.rio.transform().f, 43.4555, 3)

    def test_nearest(self):
        """Tests nearest interpolation with and without projection"""
        corner_ul = (-1.621137007661705, 43.4555890422600939)
        grid_shape = (620, 417)
        grid_res = (0.010642497622783, 0.010642497622783)

        # Test without specifying any projection, assuming the output
        # projection is the same as input
        corner_ul = (-7.2375, -4.9875)
        grid_shape = (138, 194)
        grid_res = (0.0075, 0.0075)

        grid_repr = nearest(self.data, corner_ul, grid_shape, grid_res)

        self.assertEqual(grid_repr.shape, (138, 194))

        self.assertEqual(grid_repr.rio.crs.data['proj'], 'ob_tran')
        self.assertEqual(grid_repr.rio.crs.data['o_proj'], 'longlat')
        self.assertEqual(grid_repr.rio.crs.data['o_lat_p'], 50)
        self.assertEqual(grid_repr.rio.crs.data['lon_0'], 358.5)

        self.assertAlmostEqual(grid_repr.rio.transform().a, 0.0075, 3)
        self.assertAlmostEqual(grid_repr.rio.transform().c, -7.2375, 3)
        self.assertAlmostEqual(grid_repr.rio.transform().e, -0.0075, 3)
        self.assertAlmostEqual(grid_repr.rio.transform().f, -4.9875, 3)

        self.assertNotEqual(grid_repr[2][4], None)

        # Test with a specified projection
        corner_ul = (-1.621137007661705, 43.4555890422600939)
        grid_shape = (620, 417)
        grid_res = (0.010642497622783, 0.010642497622783)
        grid_repr = bilinear(self.data, corner_ul, grid_shape, grid_res,
                             dest_proj='EPSG:4326')

        self.assertEqual(grid_repr.shape, (620, 417))
        self.assertEqual(grid_repr.rio.crs.data['init'], 'epsg:4326')
        self.assertAlmostEqual(grid_repr.rio.transform().a, 0.0106, 3)
        self.assertAlmostEqual(grid_repr.rio.transform().c, -1.6211, 3)
        self.assertAlmostEqual(grid_repr.rio.transform().e, -0.0106, 3)
        self.assertAlmostEqual(grid_repr.rio.transform().f, 43.4555, 3)

        self.assertNotEqual(grid_repr[2][4], None)
