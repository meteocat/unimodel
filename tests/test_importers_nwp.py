"""Tests transformation of NWP grib to xarray."""
import unittest

from rasterio import Affine

from importers_nwp import (read_bolam_grib, read_icon_grib, read_moloch_grib,
                           read_wrf_prs, read_arome_grib, read_arpege_grib)


class TestImportersNWP(unittest.TestCase):
    """Tests NWP grib to xarray."""
    def test_read_wrf_prs(self):
        """Test WRF grib to xarray."""
        file='tests/data/WRFPRS-03.2023020600_032.grib'
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
    
        self.assertAlmostEqual(data_var.rio.transform().a, 3000.0)
        self.assertAlmostEqual(data_var.rio.transform().b, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().c, -252466.8378711785)
        self.assertAlmostEqual(data_var.rio.transform().d, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().e, 3000.0)
        self.assertAlmostEqual(data_var.rio.transform().f, -385561.89591748564)

    def test_read_icon(self):
        """Function to test the NWP reads"""
        file='tests/data/icon-07.2023020700_10.grib2'
        variable='tp'
        data_var = read_icon_grib(file,variable)

        self.assertEqual(data_var.rio.crs.data['proj'],'longlat')
        self.assertEqual(data_var.rio.crs.data['datum'],'WGS84')

        self.assertEqual(data_var.x.shape[0],337)
        self.assertEqual(data_var.y.shape[0],209)

        self.assertAlmostEqual(data_var.values[33][13],0.032226562)
        self.assertAlmostEqual(data_var.values[13][33],0.4423828)
    
        self.assertAlmostEqual(data_var.rio.transform().a, 0.0625)
        self.assertAlmostEqual(data_var.rio.transform().b, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().c, -12.03125)
        self.assertAlmostEqual(data_var.rio.transform().d, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().e, 0.0625)
        self.assertAlmostEqual(data_var.rio.transform().f, 33.96875)





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

        self.assertAlmostEqual(moloch_data.rio.transform().a, 0.014)
        self.assertAlmostEqual(moloch_data.rio.transform().c, -0.007)
        self.assertAlmostEqual(moloch_data.rio.transform().e, 0.014)
        self.assertAlmostEqual(moloch_data.rio.transform().f, -1.5)

        self.assertAlmostEqual(moloch_data.data[5, 70], 13.779, 2)
        self.assertAlmostEqual(moloch_data.data[70, 5], 32.943, 2)

    def test_read_bolam_grib(self):
        """Tests Bolam grib to xarray."""
        bolam_data = read_bolam_grib(
            'tests/data/bolam-08.2023020600_32.grib2', 'tp')
        
        self.assertEqual(bolam_data.shape, (138, 194))

        self.assertEqual(bolam_data.rio.crs.data['proj'], 'ob_tran')
        self.assertEqual(bolam_data.rio.crs.data['o_proj'], 'longlat')
        self.assertEqual(bolam_data.rio.crs.data['o_lat_p'], 50)
        self.assertEqual(bolam_data.rio.crs.data['lon_0'], 358.5)
        self.assertEqual(bolam_data.rio.crs.data['o_lon_p'], 0)

        self.assertAlmostEqual(bolam_data.rio.transform().a, 0.075)
        self.assertAlmostEqual(bolam_data.rio.transform().c, -7.275)
        self.assertAlmostEqual(bolam_data.rio.transform().e, 0.075)
        self.assertAlmostEqual(bolam_data.rio.transform().f, -5.025)

        self.assertAlmostEqual(bolam_data.data[20, 58], 11.087, 2)
        self.assertAlmostEqual(bolam_data.data[58, 20], 0.000, 2)


    def test_read_arome_grib(self):
        """Tests AROME grib to xarray."""
        arome_data = read_arome_grib(
            'tests/data/arome-1p1.2023021000_10.grib2', 'tp')
        self.assertEqual(arome_data.shape, (501, 751))

        self.assertEqual(arome_data.rio.crs.data['proj'], 'longlat')
        self.assertEqual(arome_data.rio.crs.data['datum'], 'WGS84')

        self.assertAlmostEqual(arome_data.rio.transform().a, 0.00999,3)
        self.assertAlmostEqual(arome_data.rio.transform().c, -1.505,3)
        self.assertAlmostEqual(arome_data.rio.transform().e, -0.00999,3)
        self.assertAlmostEqual(arome_data.rio.transform().f, 44.0049,3)

        self.assertAlmostEqual(arome_data.data[500, 749], 0.204, 2)
        self.assertAlmostEqual(arome_data.data[0, 0], 0.0, 2)

    
    def test_read_arpege_grib(self):
        """Tests ARPEGE grib to xarray."""
        arpege_data = read_arpege_grib(
            'tests/data/arpege-11.2023020900_20.grib2', 'tp')
        self.assertEqual(arpege_data.shape, (51, 76))

        self.assertEqual(arpege_data.rio.crs.data['proj'], 'longlat')
        self.assertEqual(arpege_data.rio.crs.data['datum'], 'WGS84')

        self.assertAlmostEqual(arpege_data.rio.transform().a, 0.0999,3)
        self.assertAlmostEqual(arpege_data.rio.transform().c, -1.55,3)
        self.assertAlmostEqual(arpege_data.rio.transform().e, -0.1,3)
        self.assertAlmostEqual(arpege_data.rio.transform().f, 44.05,3)

        self.assertAlmostEqual(arpege_data.data[50, 73], 6.205, 2)
        self.assertAlmostEqual(arpege_data.data[3, 3], 0.0, 2)
