import unittest
import pickle
from unimodel.utils.geotools import proj4_from_grib
import pyproj




class TestGeoTools(unittest.TestCase):



    def test_geotools(self):
        # open a file, where you stored the pickled data
        with open('tests/data/xarray_geotools.pkl', 'rb') as file:
            # dump information to that file
            data = pickle.load(file)
            # close the file
        projparams = proj4_from_grib(data)
        crs_xarray = pyproj.crs.CRS.from_dict(projparams)
        pass