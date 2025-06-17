"""Tests downscaling interpolation module."""

import unittest

import numpy as np
import xarray

from unimodel.utils.xarray_tools import expand_valid_time_coord


class TestXarrayTools(unittest.TestCase):
    """Tests different interpolation methodologies"""

    arome_0 = xarray.open_dataset(
        "tests/data/list_arome_xarray_0.nc", decode_timedelta=True
    )["tp"]
    arome_1 = xarray.open_dataset(
        "tests/data/list_arome_xarray_1.nc", decode_timedelta=True
    )["tp"]
    data = [arome_0, arome_1]

    concat_data = xarray.open_dataset(
        "tests/data/concat_xarray.nc", decode_timedelta=True
    )["tp"]

    def test_expand_valid_time_coord(self):
        """Tests expand time coordinate utility"""
        xarray_padded = expand_valid_time_coord(self.data[0], lead_time=72, interval=1)

        self.assertEqual(xarray_padded.shape, (72, 417, 620))
        self.assertEqual(
            xarray_padded.valid_time[0], np.datetime64("2023-02-15T03:00:00.000000000")
        )
        self.assertEqual(
            xarray_padded.valid_time[-1], np.datetime64("2023-02-18T02:00:00.000000000")
        )
        self.assertEqual(
            xarray_padded.valid_time[8], np.datetime64("2023-02-15T11:00:00.000000000")
        )
        self.assertAlmostEqual(float(xarray_padded[0][200][200].data), 0.0)
        self.assertTrue(np.isnan(xarray_padded[8][200][200].data))

        xarray_padded = expand_valid_time_coord(self.data[0], lead_time=72, interval=6)

        self.assertEqual(xarray_padded.shape, (12, 417, 620))
        self.assertEqual(
            xarray_padded.valid_time[0], np.datetime64("2023-02-15T03:00:00.000000000")
        )
        self.assertEqual(
            xarray_padded.valid_time[-1], np.datetime64("2023-02-17T21:00:00.000000000")
        )
        self.assertEqual(
            xarray_padded.valid_time[8], np.datetime64("2023-02-17T03:00:00.000000000")
        )
        self.assertAlmostEqual(float(xarray_padded[0][200][200].data), 0.0)
        self.assertTrue(np.isnan(xarray_padded[8][200][200].data))

        xarray_padded = expand_valid_time_coord(
            self.concat_data, lead_time=72, interval=1
        )
        self.assertEqual(xarray_padded.shape, (72, 417, 620))
        self.assertEqual(
            xarray_padded.valid_time[0], np.datetime64("2023-02-15T03:00:00.000000000")
        )
        self.assertEqual(
            xarray_padded.valid_time[1], np.datetime64("2023-02-15T04:00:00.000000000")
        )
        self.assertEqual(
            xarray_padded.valid_time[-1], np.datetime64("2023-02-18T02:00:00.000000000")
        )
        self.assertAlmostEqual(float(xarray_padded[0][200][200].data), 0.0)
        self.assertTrue(np.isnan(xarray_padded[8][200][200].data))

    def test_expand_valid_time_coord_wrong_interval(self):
        """Tests interval different than data temporal resolution"""
        with self.assertRaises(ValueError) as err:
            expand_valid_time_coord(self.concat_data, lead_time=72, interval=6)

        self.assertEqual(
            "'interval' is different than temporal resolution of data.",
            err.exception.args[0],
        )

    def test_expand_valid_time_coord_multiple_interval(self):
        """Tests lead_time not multiple of interval"""
        with self.assertRaises(ValueError) as err:
            expand_valid_time_coord(self.data[0], lead_time=65, interval=6)

        self.assertEqual(
            "'lead_time' is not a multiple of 'interval'. "
            "Padding of xarray is discarded.",
            err.exception.args[0],
        )

    def test_expand_valid_time_coord_valid_time_not_found(self):
        """Tests valid_time not in data"""
        data = self.data[0].drop_vars("valid_time")
        with self.assertRaises(KeyError) as err:
            expand_valid_time_coord(data, lead_time=65, interval=1)

        self.assertEqual("'valid_time' not in data coordinates.", err.exception.args[0])
