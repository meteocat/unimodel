"""Tests downscaling interpolation module.
"""
import pickle
import unittest
import numpy as np

from unimodel.utils.pad_xarray import pad_xarray

class Test_Pad_xarary(unittest.TestCase):
    """Tests different interpolation methodologies."""
    with open('tests/data/xarray_model.pkl', 'rb') as file:
        data = pickle.load(file)

    def test_pad_xarray(self):
        xarray_padded = pad_xarray(self.data, lead_times=72, time_span=1)

        self.assertEqual(xarray_padded[0].shape[0], 138)
        self.assertEqual(xarray_padded[0].shape[1], 194)

        self.assertAlmostEqual(float(xarray_padded[0][2][4].data), 0.0)
        self.assertTrue(np.isnan(xarray_padded[4][2][4].data))

