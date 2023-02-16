
import pickle
import unittest
from unimodel.downscaling.interpolation import (bilinear, nearest)

class TestInterpolation(unittest.TestCase):
    # open a file, where you stored the pickled data
    with open('tests/data/xarray_model.pkl', 'rb') as file:
        # dump information to that file
        data = pickle.load(file)


    def test_bilinear(self):
        """Testejem la interpolació nearest amb i sense projectar"""  
 
        
        # Test sense projeccio
        corner_ul = (-7.2375,-4.9875)
        grid_shape = (138, 194)
        grid_res = (0.0075, 0.0075)

        grid_repr = bilinear(self.data, corner_ul, 
                                grid_shape, grid_res) 

        self.assertEqual(grid_repr.shape, (138, 194))

        self.assertEqual(grid_repr.rio.crs.data['proj'], 'ob_tran')
        self.assertEqual(grid_repr.rio.crs.data['o_proj'], 'longlat')
        self.assertEqual(grid_repr.rio.crs.data['o_lat_p'], 50)
        self.assertEqual(grid_repr.rio.crs.data['lon_0'], 358.5)

        self.assertAlmostEqual(grid_repr.rio.transform().a, 0.0075,3)
        self.assertAlmostEqual(grid_repr.rio.transform().c, -7.2375,3)
        self.assertAlmostEqual(grid_repr.rio.transform().e, 0.0075,3)
        self.assertAlmostEqual(grid_repr.rio.transform().f, -4.9875,3) 


         # Test amb projeccio
        corner_ul = (-1.621137007661705,43.4555890422600939)
        grid_shape = (620, 417)
        grid_res = (0.010642497622783, 0.010642497622783)
        grid_repr = bilinear(self.data, corner_ul, 
                             grid_shape, grid_res,
                             dest_proj='EPSG:4326' )
        self.assertEqual(grid_repr.shape, (620, 417))

        self.assertEqual(grid_repr.rio.crs.data['init'], 'epsg:4326')

        self.assertAlmostEqual(grid_repr.rio.transform().a, 0.0106,3)
        self.assertAlmostEqual(grid_repr.rio.transform().c, -1.6211,3)
        self.assertAlmostEqual(grid_repr.rio.transform().e, 0.0106424,3)
        self.assertAlmostEqual(grid_repr.rio.transform().f, 43.4555,3)         


    def test_nearest(self):
        """Testejem la interpolació nearest amb i sense projectar"""      
          
        corner_ul = (-1.621137007661705,43.4555890422600939)
        grid_shape = (620, 417)
        grid_res = (0.010642497622783, 0.010642497622783)

        # Test sense projeccio
        corner_ul = (-7.2375,-4.9875)
        grid_shape = (138, 194)
        grid_res = (0.0075, 0.0075)

        grid_repr = bilinear(self.data, corner_ul, 
                                grid_shape, grid_res) 

        self.assertEqual(grid_repr.shape, (138, 194))

        self.assertEqual(grid_repr.rio.crs.data['proj'], 'ob_tran')
        self.assertEqual(grid_repr.rio.crs.data['o_proj'], 'longlat')
        self.assertEqual(grid_repr.rio.crs.data['o_lat_p'], 50)
        self.assertEqual(grid_repr.rio.crs.data['lon_0'], 358.5)

        self.assertAlmostEqual(grid_repr.rio.transform().a, 0.0075,3)
        self.assertAlmostEqual(grid_repr.rio.transform().c, -7.2375,3)
        self.assertAlmostEqual(grid_repr.rio.transform().e, 0.0075,3)
        self.assertAlmostEqual(grid_repr.rio.transform().f, -4.9875,3) 

        self.assertNotEqual(grid_repr[2][4],None)


         # Test amb projeccio
        corner_ul = (-1.621137007661705,43.4555890422600939)
        grid_shape = (620, 417)
        grid_res = (0.010642497622783, 0.010642497622783)
        grid_repr = bilinear(self.data, corner_ul, 
                             grid_shape, grid_res,
                             dest_proj='EPSG:4326' )
        self.assertEqual(grid_repr.shape, (620, 417))

        self.assertEqual(grid_repr.rio.crs.data['init'], 'epsg:4326')

        self.assertAlmostEqual(grid_repr.rio.transform().a, 0.0106,3)
        self.assertAlmostEqual(grid_repr.rio.transform().c, -1.6211,3)
        self.assertAlmostEqual(grid_repr.rio.transform().e, 0.0106424,3)
        self.assertAlmostEqual(grid_repr.rio.transform().f, 43.4555,3)

        self.assertNotEqual(grid_repr[2][4],None)