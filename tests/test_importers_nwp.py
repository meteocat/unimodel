import unittest
from rasterio import Affine

from importers_nwp import read_wrf_prs
from importers_nwp import read_icon


class TestIOImportNwp(unittest.TestCase):

   
    def test_read_wrf_prs(self):
        """Function to test the NWP reads"""
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


    def test_read_icon(self):
        """Function to test the NWP reads"""
        file='/home/jmc/workspace/unimodel/tests/data/icon-07.2023020700_10.grib2'
        variable='tp'
        data_var = read_icon(file,variable)

        self.assertEqual(data_var.rio.crs.data['proj'],'longlat')
        self.assertEqual(data_var.rio.crs.data['datum'],'WGS84')

        self.assertEqual(data_var.x.shape[0],337)
        self.assertEqual(data_var.y.shape[0],209)

        self.assertAlmostEqual(data_var.values[33][13],0.032226562)
        self.assertAlmostEqual(data_var.values[13][33],0.4423828)
    
        self.assertAlmostEqual(data_var.rio.transform(),
                               Affine(0.0625, 0.0, -12.03125,
                                      0.0, -0.0625, 34.03125))