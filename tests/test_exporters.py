"""Tests of constructing a netcdf from an xarray list
"""
import pickle
import unittest

import xarray

from unimodel.io.exporters import export_to_netcdf


class TestExportersNWP(unittest.TestCase):
    """Tests list array to netcdf."""
    def test_exporters_to_netcdf(self):

        variable='tp'
        netcdf_file='tests/data/out/reproject_models.nc'

        with open('tests/data/list_arome_xarray.pkl', 'rb') as file:
            list_arome_xarrays = pickle.load(file)
        with open('tests/data/list_bolam_xarray.pkl', 'rb') as file:
            list_bolam_xarrays = pickle.load(file)
    
        list_models_arrays=[list_arome_xarrays, list_bolam_xarrays]
        export_to_netcdf(netcdf_file, list_models_arrays, var=variable)

        netcdf_data= xarray.open_dataset(netcdf_file)

        self.assertEqual(netcdf_data.dims['x'], 
                         list_bolam_xarrays[0].x.shape[0])
        self.assertEqual(netcdf_data.dims['y'], 
                         list_bolam_xarrays[0].y.shape[0])
        

        self.assertAlmostEqual(netcdf_data.rio.transform().a, 
                               list_bolam_xarrays[0].rio.transform().a)
        self.assertAlmostEqual(netcdf_data.rio.transform().b, 
                               list_bolam_xarrays[0].rio.transform().b)
        self.assertAlmostEqual(netcdf_data.rio.transform().c, 
                               list_bolam_xarrays[0].rio.transform().c)
        self.assertAlmostEqual(netcdf_data.rio.transform().d, 
                               list_bolam_xarrays[0].rio.transform().d)
        self.assertAlmostEqual(netcdf_data.rio.transform().e, 
                               list_bolam_xarrays[0].rio.transform().e)
        self.assertAlmostEqual(netcdf_data.rio.transform().f, 
                               list_bolam_xarrays[0].rio.transform().f)



        
