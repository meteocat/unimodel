"""Tests exporters module.
"""
import pickle
import unittest

from unimodel.downscaling.ecorrection import Ecorrection

config = {'hres_dem_file': 'tests/data/neighbours_wrf3_ecm.npz', 'neighbours_file': 'tests/data/hres_dem_25831.tif'}
config_wrong = {'hres_dem_file': 'ecorr/tests/data/not_found.tif'}

class TestEcorrection(unittest.TestCase):

    def test_init(self):

        Ecorrection('2t', config)


