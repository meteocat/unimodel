"""Tests exporters module.
"""
import pickle
import unittest

from unimodel.downscaling.ecorrection import Ecorrection

config = {'hres_dem_file': '', 'neighbours_file': ''}
config_wrong = {'hres_dem_file': 'ecorr/tests/data/not_found.tif'}

class TestEcorrection(unittest.TestCase):

    def test_init(self):

        Ecorrection('2t', config)


