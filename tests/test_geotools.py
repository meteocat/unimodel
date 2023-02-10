import pickle
import unittest

import pyproj

from unimodel.utils.geotools import proj4_from_grib


class TestGeoTools(unittest.TestCase):
    """Test geotools"""

    def test_proj4_from_grib(self):
        """Test getting proj4"""
        # open a file, where you stored the pickled data
        with open('tests/data/xarray_geotools.pkl', 'rb') as file:
            # dump information to that file
            data = pickle.load(file)
            # close the file
        projparams = proj4_from_grib(data)
        crs_xarray = pyproj.crs.CRS.from_dict(projparams)
        self.assertEqual(projparams['proj'],'lcc')
        self.assertEqual(projparams['lat_0'],30)
        self.assertEqual(projparams['lat_2'],60)
        self.assertEqual(crs_xarray.to_json_dict()['base_crs']['datum']['ellipsoid']['name'],
                         'WGS 84')
