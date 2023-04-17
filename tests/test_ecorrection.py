"""Tests exporters module.
"""
import pickle
import unittest

from unimodel.downscaling.ecorrection import Ecorrection

class TestEcorrection(unittest.TestCase):

    config = {'hres_dem_file': 'tests/data/test_data/hres_dummy.txt', 'neighbours_file': 'tests/data/test_data/neighbours_dummy.txt'}
    config_wrong = {'hres_dem_file': 'ecorr/tests/data/not_found.tif'}

    def test_init(self):

        # ecor = Ecorrection('2t', self.config)

        with self.assertRaises(KeyError) as err:

            Ecorrection('2t', self.config_wrong)

        with self.assertRaises(ValueError) as err:

            Ecorrection('2d', self.config)

        with self.assertRaises(FileNotFoundError) as err:

            Ecorrection('2t', self.config)
