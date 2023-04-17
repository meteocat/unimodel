"""Tests exporters module.
"""
import pickle
import unittest

from unimodel.downscaling.ecorrection import Ecorrection

class TestEcorrection(unittest.TestCase):

    config = {'hres_dem_file': 'tests/data/test_data/hres_dummy.txt', 'neighbours_file': 'tests/data/test_data/neighbours_dummy.txt'}
    config_wrong = {'hres_dem_file': 'tests/data/test_data/hres_dummy.txt'}
    config_nofile = {'hres_dem_file': 'tests/data/test_data/nofile.txt', 'neighbours_file': 'tests/data/test_data/nofile.txt'}

    def test_init_not_2t_variable(self):

        with self.assertRaises(ValueError) as err:

            Ecorrection('2d', self.config)

        self.assertEqual(err.exception.args[0], "2d must be '2t'")

    def test_init_config_dict(self):

        with self.assertRaises(KeyError) as err:

            Ecorrection('2t', self.config_wrong)

        self.assertEqual(err.exception.args[0],"At least 'hres_dem_file' and 'neighbours_file' must be in the config dictionary")

    def test_init_file_not_found(self):

        with self.assertRaises(FileNotFoundError) as err:

            Ecorrection('2t', self.config_nofile)

        self.assertEqual(err.exception.args[0], f'{self.config_nofile["hres_dem_file"]} not found')
   

        
