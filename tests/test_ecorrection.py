"""Tests ecorrection class
"""
import pickle
import unittest

from unimodel.io.readers_nwp import read_wrf_prs
from unimodel.downscaling.ecorrection import Ecorrection


class TestEcorrection(unittest.TestCase):
    """Test function to apply elevation correction to a given xarray
    """
    config = {'hres_dem_file': 'tests/data/test_data/hres_dem_25831.tif',
              'neighbours_file': 'tests/data/test_data/neighbours_dummy.txt'}
    config_wrong = {'hres_dem_file': 'tests/data/test_data/hres_dummy.txt'}
    config_nofile = {'hres_dem_file': 'tests/data/test_data/nofile.txt',
                     'neighbours_file': 'tests/data/test_data/nofile.txt'}

    def test_init(self):
        """Tests function to initialize the object's attributes
        """
        ecor = Ecorrection('2t', self.config)

        self.assertEqual(ecor.variable, '2t')
        self.assertEqual(ecor.config, self.config)


    def test_init_not_2t_variable(self):
        """Wrong input variable  
        """
        with self.assertRaises(ValueError) as err:

            Ecorrection('2d', self.config)

        self.assertEqual(err.exception.args[0], "2d must be '2t'")


    def test_init_config_dict(self):
        """Config dictionary without mandatory keys  
        """
        with self.assertRaises(KeyError) as err:

            Ecorrection('2t', self.config_wrong)

        self.assertEqual(err.exception.args[0],"At least 'hres_dem_file' and"
                         "'neighbours_file' must be in the config dictionary")


    def test_init_hres_dem_not_found(self):
        """High resolution DEM file not found
        """
        with self.assertRaises(FileNotFoundError) as err:

            Ecorrection('2t', self.config_nofile)

        self.assertEqual(err.exception.args[0], f'{self.config_nofile["hres_dem_file"]} not found')


    def test_get_neighbours(self):
        """Tests function for calculate neighbours 
        """
        with open('tests/data/test_data/lsm_xarray.pkl', 'rb') as file:
            
            da_lsm = pickle.load(file)
            file.close()

        out_file = 'tests/data/test_data/neighbours.npz'

        ecor = Ecorrection('2t', self.config)
        neigh = ecor.get_neighbours(land_binary_mask=da_lsm, out_file=out_file, neighbours=64)

        self.assertEqual(neigh.keys(), 
                         dict.fromkeys(['indices', 'neigh_needed', 'neigh_candidates']).keys())

    def test_get_neighbours_lsm_not_found(self):
        """Land binary mask dataArray not found
        """
        da_lsm_wrong = read_wrf_prs('tests/data/nwp_src/wrf43_prs/WRFPRS-03.2023020600_032.grib',
                                    '2t', 'WRF')
        out_file = 'tests/data/test_data/neighbours.npz'

        with self.assertRaises(ValueError) as err:
            
            ecor = Ecorrection('2t', self.config)
            ecor.get_neighbours(land_binary_mask=da_lsm_wrong, out_file=out_file, neighbours=64)

        self.assertEqual(err.exception.args[0], '\'land_binary_mask\' variable does not exist')
   