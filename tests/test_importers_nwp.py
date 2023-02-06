import unittest

from importers_nwp import read_wrf_prs


class TestIOImportNwp(unittest.TestCase):

   
    def test_io_import_nwp_grib(self):
        file='/home/jmc/workspace/unimodel/tests/data/WRFPRS-03.2023020600_032.grib'
        data_var = read_wrf_prs(file)

        self.assertEqual(data_var.rio.crs.data['proj'],'lcc')
        self.assertEqual(data_var.rio.crs.data['lat_1'],60)
        self.assertEqual(data_var.rio.crs.data['lat_2'],30)
        self.assertEqual(data_var.rio.crs.data['lat_0'],40.70002)
        self.assertEqual(data_var.rio.crs.data['lon_0'], -1.5)

        self.assertEqual(data_var.x.shape[0],299)
        self.assertEqual(data_var.y.shape[0],259)

        self.assertAlmostEqual(data_var.values[120][133],1.97)
        self.assertAlmostEqual(data_var.values[133][120],0.14)

        



