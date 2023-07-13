"""Tests transformation of NWP grib to xarray.
"""
import unittest
import os

from unimodel.io.readers_nwp import (read_arome_grib, read_arpege_grib,
                                     read_bolam_grib, read_ecmwf_hres_grib,
                                     read_ecmwf_ens_grib, read_icon_grib,
                                     read_moloch_grib, read_unified_model_grib,
                                     read_wrf_prs, read_wrf_tl_ens_grib)


class TestReadersNWP(unittest.TestCase):
    """Tests NWP grib to xarray"""

    def test_read_wrf_prs(self):
        """Test WRF grib to xarray"""
        file = 'tests/data/nwp_src/wrf43_prs/WRFPRS-03.2023020600_032.grib'
        file_idx = file + '.02ccc.idx'
        variable = 'tp'
        model = 'wrf'
        data_var = read_wrf_prs(file, variable, model)

        self.assertEqual(data_var.rio.crs.data['proj'], 'lcc')
        self.assertEqual(data_var.rio.crs.data['lat_1'], 60)
        self.assertEqual(data_var.rio.crs.data['lat_2'], 30)
        self.assertEqual(data_var.rio.crs.data['lat_0'], 40.70002)
        self.assertEqual(data_var.rio.crs.data['lon_0'], -1.5)

        self.assertEqual(data_var.x.shape[0], 299)
        self.assertEqual(data_var.y.shape[0], 259)

        self.assertAlmostEqual(data_var.values[120][133], 1.97)
        self.assertAlmostEqual(data_var.values[133][120], 0.14)

        self.assertAlmostEqual(data_var.rio.transform().a, 3000.0)
        self.assertAlmostEqual(data_var.rio.transform().b, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().c, -252466.8378711785)
        self.assertAlmostEqual(data_var.rio.transform().d, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().e, 3000.0)
        self.assertAlmostEqual(data_var.rio.transform().f, -385561.89591748564)

        self.assertFalse(os.path.isfile(file_idx))

    def test_read_wrf_prs_gfs_9(self):
        """Test WRF grib to xarray"""
        file = 'tests/data/nwp_src/wrf_gfs_9/WRFPRS_d01.000'
        file_idx = file + '.02ccc.idx'
        variable = 'tp'
        model = 'wrf_gfs_9'
        data_var = read_wrf_prs(file, variable, model)

        self.assertEqual(data_var.rio.crs.data['proj'], 'lcc')
        self.assertEqual(data_var.rio.crs.data['lat_1'], 60)
        self.assertEqual(data_var.rio.crs.data['lat_2'], 30)
        self.assertEqual(data_var.rio.crs.data['lat_0'], 40.70002)
        self.assertEqual(data_var.rio.crs.data['lon_0'], -1.5)

        self.assertEqual(data_var.x.shape[0], 199)
        self.assertEqual(data_var.y.shape[0], 149)

        self.assertAlmostEqual(data_var.values[120][133], 0.0)
        self.assertAlmostEqual(data_var.values[133][120], 0.0)

        self.assertAlmostEqual(data_var.rio.transform().a, 9000.0)
        self.assertAlmostEqual(data_var.rio.transform().b, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().c, -699466.8009145432)
        self.assertAlmostEqual(data_var.rio.transform().d, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().e, 9000.0)
        self.assertAlmostEqual(data_var.rio.transform().f, -667561.8777376108)

        self.assertFalse(os.path.isfile(file_idx))

    def test_read_icon(self):
        """Function to test the NWP reads"""
        file = 'tests/data/nwp_src/icon/icon-07.2023020700_10.grib2'
        file_idx = file + '.02ccc.idx'
        variable = 'tp'
        model = 'icon'
        data_var = read_icon_grib(file, variable, model)

        self.assertEqual(data_var.rio.crs.data['proj'], 'longlat')
        self.assertEqual(data_var.rio.crs.data['datum'], 'WGS84')

        self.assertEqual(data_var.x.shape[0], 337)
        self.assertEqual(data_var.y.shape[0], 209)

        self.assertAlmostEqual(data_var.values[33][13], 0.032226562)
        self.assertAlmostEqual(data_var.values[13][33], 0.4423828)

        self.assertAlmostEqual(data_var.rio.transform().a, 0.0625)
        self.assertAlmostEqual(data_var.rio.transform().b, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().c, -12.03125)
        self.assertAlmostEqual(data_var.rio.transform().d, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().e, 0.0625)
        self.assertAlmostEqual(data_var.rio.transform().f, 33.96875)

        self.assertFalse(os.path.isfile(file_idx))

    def test_read_moloch_grib(self):
        """Tests Moloch grib to xarray"""
        file = 'tests/data/nwp_src/moloch/moloch-1p6.2022032100_48.grib2'
        file_idx = file + '.02ccc.idx'
        variable = 'tp'
        model = 'moloch'
        moloch_data = read_moloch_grib(file, variable, model)

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

        self.assertFalse(os.path.isfile(file_idx))

    def test_read_bolam_grib(self):
        """Tests Bolam grib to xarray"""
        file = 'tests/data/nwp_src/bolam/bolam-08.2023020600_32.grib2'
        file_idx = file + '.02ccc.idx'
        variable = 'tp'
        model = 'bolam'
        bolam_data = read_bolam_grib(file, variable, model)

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

        self.assertFalse(os.path.isfile(file_idx))

    def test_read_arome_grib(self):
        """Tests AROME grib to xarray"""
        file = 'tests/data/nwp_src/arome/arome-1p1.2023021000_10.grib2'
        file_idx = file + '.02ccc.idx'
        variable = 'tp'
        model = 'arome'
        arome_data = read_arome_grib(file, variable, model)

        self.assertEqual(arome_data.shape, (501, 751))

        self.assertEqual(arome_data.rio.crs.data['proj'], 'longlat')
        self.assertEqual(arome_data.rio.crs.data['datum'], 'WGS84')

        self.assertAlmostEqual(arome_data.rio.transform().a, 0.00999, 3)
        self.assertAlmostEqual(arome_data.rio.transform().c, -1.505, 3)
        self.assertAlmostEqual(arome_data.rio.transform().e, -0.00999, 3)
        self.assertAlmostEqual(arome_data.rio.transform().f, 44.0049, 3)

        self.assertAlmostEqual(arome_data.data[500, 749], 0.204, 2)
        self.assertAlmostEqual(arome_data.data[0, 0], 0.0, 2)

        self.assertFalse(os.path.isfile(file_idx))

    def test_read_arpege_grib(self):
        """Tests ARPEGE grib to xarray"""
        file = 'tests/data/nwp_src/arpege/arpege-11.2023020900_20.grib2'
        file_idx = file + '.02ccc.idx'
        variable = 'tp'
        model = 'arpege'
        arpege_data = read_arpege_grib(file, variable, model)

        self.assertEqual(arpege_data.shape, (51, 76))

        self.assertEqual(arpege_data.rio.crs.data['proj'], 'longlat')
        self.assertEqual(arpege_data.rio.crs.data['datum'], 'WGS84')

        self.assertAlmostEqual(arpege_data.rio.transform().a, 0.0999, 3)
        self.assertAlmostEqual(arpege_data.rio.transform().c, -1.55, 3)
        self.assertAlmostEqual(arpege_data.rio.transform().e, -0.1, 3)
        self.assertAlmostEqual(arpege_data.rio.transform().f, 44.05, 3)

        self.assertAlmostEqual(arpege_data.data[50, 73], 6.205, 2)
        self.assertAlmostEqual(arpege_data.data[3, 3], 0.0, 2)

        self.assertFalse(os.path.isfile(file_idx))

    def test_read_ecmwf_hres_grib(self):
        """Tests ECMWF-HRES grib to xarray"""
        file = 'tests/data/nwp_src/ecmwf/A1S02200000022006001'
        file_idx = file + '.02ccc.idx'
        variable = 'tp'
        data_var = read_ecmwf_hres_grib(file, variable, 'ecmwf_hres')

        self.assertEqual(data_var.rio.crs.data['proj'], 'longlat')
        self.assertEqual(data_var.rio.crs.data['datum'], 'WGS84')

        self.assertEqual(data_var.x.shape[0], 211)
        self.assertEqual(data_var.y.shape[0], 131)

        self.assertAlmostEqual(data_var.values[50, 80], 0.503, 2)
        self.assertAlmostEqual(data_var.values[80, 50], 0.0)

        self.assertAlmostEqual(data_var.rio.transform().a, 0.1)
        self.assertAlmostEqual(data_var.rio.transform().b, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().c, -12.05)
        self.assertAlmostEqual(data_var.rio.transform().d, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().e, -0.1)
        self.assertAlmostEqual(data_var.rio.transform().f, 47.05)

        self.assertFalse(os.path.isfile(file_idx))

    def test_read_ecmwf_ens_grib(self):
        """Tests ECMWF-ENS grib to xarray"""
        file = 'tests/data/nwp_src/ecmwf/A4E07050000070501001'
        file_idx = file + '.02ccc.idx'
        variable = 'tp'
        ens_type = 'pf'
        data_var = read_ecmwf_ens_grib(file, variable, ens_type, 'ecmwf_ens')

        self.assertEqual(data_var.rio.crs.data['proj'], 'longlat')
        self.assertEqual(data_var.rio.crs.data['datum'], 'WGS84')

        self.assertEqual(data_var.x.shape[0], 66)
        self.assertEqual(data_var.y.shape[0], 46)

        self.assertAlmostEqual(data_var.values[2, 11, 16], 1.385, 2)
        self.assertAlmostEqual(data_var.values[2, 0, 6], 0.0)

        self.assertAlmostEqual(data_var.rio.transform().a, 0.1)
        self.assertAlmostEqual(data_var.rio.transform().b, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().c, -1.55)
        self.assertAlmostEqual(data_var.rio.transform().d, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().e, -0.1)
        self.assertAlmostEqual(data_var.rio.transform().f, 43.55)

        self.assertFalse(os.path.isfile(file_idx))

        bad_ens_type = 'control'
        with self.assertRaises(ValueError) as err:
            read_ecmwf_ens_grib(file, variable, bad_ens_type, 'ecmwf_ens')

        self.assertEqual(err.exception.args[0],
                         '\'ens_type\' must be \'cf\' for control forecast '
                         'or \'pf\' for perturbed forecast')

    def test_read_unified_model_grib(self):
        """Tests Unified Model grib to xarray"""
        file = 'tests/data/nwp_src/um/um-10.2023032700_03.grib2'
        file_idx = file + '.02ccc.idx'
        variable = 'tp'
        model = 'um'
        um_data = read_unified_model_grib(file, variable, model)

        self.assertEqual(um_data.shape, (138, 149))

        self.assertEqual(um_data.rio.crs.data['proj'], 'longlat')
        self.assertEqual(um_data.rio.crs.data['datum'], 'WGS84')

        self.assertAlmostEqual(um_data.rio.transform().a, 0.140625, 3)
        self.assertAlmostEqual(um_data.rio.transform().c, -11.9531, 3)
        self.assertAlmostEqual(um_data.rio.transform().e, 0.09375, 3)
        self.assertAlmostEqual(um_data.rio.transform().f, 34.03125, 3)

        self.assertAlmostEqual(um_data.data[83, 148], 9.931, 2)
        self.assertAlmostEqual(um_data.data[137, 83], 0.0, 2)

        self.assertFalse(os.path.isfile(file_idx))

        variable = '2t'
        um_data = read_unified_model_grib(file, variable, model)

        self.assertEqual(um_data.shape, (138, 149))

    def test_read_wrf_tl_ens_grib(self):
        """Tests WRF-TL-ENS member grib to xarray"""
        file = 'tests/data/nwp_src/wrf_tl_ens/ens-002.2023032009_01.grib'
        file_idx = file + '.02ccc.idx'
        variable = 'tp'
        data_var = read_wrf_tl_ens_grib(file, variable, 'wrf_tl_ens')

        self.assertEqual(data_var.rio.crs.data['proj'], 'longlat')
        self.assertEqual(data_var.rio.crs.data['datum'], 'WGS84')
        self.assertTrue('realization' in data_var.coords)

        self.assertEqual(data_var.x.shape[0], 231)
        self.assertEqual(data_var.y.shape[0], 161)

        self.assertAlmostEqual(data_var.values[76, 160], 0.109, 2)
        self.assertAlmostEqual(data_var.values[160, 72], 0.0)

        self.assertAlmostEqual(data_var.rio.transform().a, 0.025)
        self.assertAlmostEqual(data_var.rio.transform().b, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().c, -1.2625)
        self.assertAlmostEqual(data_var.rio.transform().d, 0.0)
        self.assertAlmostEqual(data_var.rio.transform().e, 0.025)
        self.assertAlmostEqual(data_var.rio.transform().f, 39.2375)

        self.assertFalse(os.path.isfile(file_idx))
