"""Tests transformation of NWP grib to xarray."""
import unittest

from rasterio import Affine

from importers_nwp import read_moloch_grib, read_wrf_prs


class TestImportersNWP(unittest.TestCase):
    """Tests NWP grib to xarray."""
    def test_read_wrf_prs(self):
        """Test WRF grib to xarray."""
        file='/home/jmc/workspace/unimodel/tests/data/WRFPRS-03.2023020600_032.grib'
        variable='tp'
        data_var = read_wrf_prs(file,variable)

        self.assertEqual(data_var.rio.crs.data['proj'],'lcc')
        self.assertEqual(data_var.rio.crs.data['lat_1'],60)
        self.assertEqual(data_var.rio.crs.data['lat_2'],30)
        self.assertEqual(data_var.rio.crs.data['lat_0'],40.70002)
        self.assertEqual(data_var.rio.crs.data['lon_0'], -1.5)

        self.assertEqual(data_var.x.shape[0],299)
        self.assertEqual(data_var.y.shape[0],259)

        self.assertAlmostEqual(data_var.values[120][133],1.97)
        self.assertAlmostEqual(data_var.values[133][120],0.14)

        self.assertAlmostEqual(data_var.rio.transform(),
                               Affine(3000.0, 0.0, -250966.8378711785,
                                      0.0, -3000.0, 389938.10408251436))

    def test_read_moloch_grib(self):
        """Tests Moloch grib to xarray."""
        moloch_data = read_moloch_grib(
            'tests/data/moloch-1p6.2022032100_48.grib2', 'tp')

        self.assertEqual(moloch_data.shape, (370, 370))

        self.assertEqual(moloch_data.rio.crs.data['proj'], 'ob_tran')
        self.assertEqual(moloch_data.rio.crs.data['o_proj'], 'longlat')
        self.assertEqual(moloch_data.rio.crs.data['o_lat_p'], 50)
        self.assertEqual(moloch_data.rio.crs.data['lon_0'], 358.36)
        self.assertEqual(moloch_data.rio.crs.data['o_lon_p'], 0)

        self.assertEqual(moloch_data.rio.transform().a, 0.014)
        self.assertEqual(moloch_data.rio.transform().c, -0.007)
        self.assertEqual(moloch_data.rio.transform().e, 0.014)
        self.assertEqual(moloch_data.rio.transform().f, -1.5)

        self.assertAlmostEqual(moloch_data.data[5, 70], 13.779, 2)
        self.assertAlmostEqual(moloch_data.data[70, 5], 32.943, 2)
