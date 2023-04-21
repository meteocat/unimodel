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

    neigh_wrong = {'indices_wrong': 'nodata', 'neigh_needed_wrong': 'nodata', 
                   'candidates_wrong': 'nodata'}

    with open('tests/data/test_data/var_xarray.pkl', 'rb') as file:

        da_var = pickle.load(file)
        file.close()

    out_file = 'tests/data/test_data/neighbours.npz'
    da_lsm_wrong = read_wrf_prs('tests/data/nwp_src/wrf43_prs/WRFPRS-03.2023020600_032.grib',
                                '2t', 'WRF')

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

        self.assertEqual(err.exception.args[0],"At least 'hres_dem_file' and "
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
        ecor = Ecorrection('2t', self.config)
        neigh = ecor.get_neighbours(land_binary_mask=self.da_var[0],
                                    out_file=self.out_file,
                                    neighbours=64)

        self.assertEqual(neigh.keys(),
                         {'indices', 'neigh_needed', 'neigh_candidates'})


    def test_neighbours_on_land(self):
        """Tests if neighbours are on land
        """
        ecor = Ecorrection('2t', self.config)
        neigh = ecor.get_neighbours(land_binary_mask=self.da_var[0],
                                    out_file=self.out_file,
                                    neighbours=64)

        index_point = neigh['neigh_needed'].tolist().index([123,105])
        index_indices = neigh['indices'][index_point]
        test_point = neigh['neigh_candidates'][index_indices].tolist()

        for i in range(64):

            self.assertEqual(self.da_var[0][test_point[i][0], test_point[i][1]].values, 1.0)


    def test_get_neighbours_lsm_not_found(self):
        """Land binary mask dataArray not found
        """
        with self.assertRaises(ValueError) as err:

            ecor = Ecorrection('2t', self.config)
            ecor.get_neighbours(land_binary_mask=self.da_lsm_wrong,
                                out_file=self.out_file,
                                neighbours=64)

        self.assertEqual(err.exception.args[0], '\'land_binary_mask\' variable does not exist')


    def test_calculate_lapse_rate(self):
        """Tests Calculate_lapse_rate function
        """

    def test_lapse_rate_neighbours_dict(self):
        """Neighbours dictionary without mandatory keys 
        """
        with self.assertRaises(KeyError) as err:

            ecor = Ecorrection('2t', self.config)
            ecor.calculate_lapse_rate(self.neigh_wrong, self.da_var[1], self.da_var[2])

        self.assertEqual(err.exception.args[0], "'indices', 'neigh_needed' and 'neigh_candidates' "
                         "must be in the neigh_info dictionary")


    def test_lapse_rate_not_2t_dataaray(self):
        """datarray without the desired variable (2t)
        """



    def test_lapse_rate_not_height_dataaray(self):
        """Datarray without the desired variable (height)
        """

   