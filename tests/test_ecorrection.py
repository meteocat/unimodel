"""Tests ecorrection class
"""
import pickle
import unittest
import xarray as xr
import numpy as np

from unimodel.downscaling.ecorrection import Ecorrection


class TestEcorrection(unittest.TestCase):
    """Test function to apply elevation correction to a given xarray
    """
    dem_file = 'tests/data/test_data/hres_dem_25831.tif'
    dem_file_wrong = 'tests/data/hres_dem_25831.tif'

    with open('tests/data/test_data/var_xarray.pkl', 'rb') as file:

        da_var = pickle.load(file)
        file.close()

    def test_init(self):
        """Tests function to initialize the object's attributes
        """
        ecor = Ecorrection(self.da_var[0], self.dem_file)

        xr.testing.assert_equal(ecor.land_binary_mask, self.da_var[0])


    def test_init_not_land_binary_mask(self):
        """Wrong 'land_binary_mask' variable
        """
        with self.assertRaises(ValueError) as err:

            Ecorrection(self.da_var[1], self.dem_file)

        self.assertEqual(err.exception.args[0], "'land_binary_mask' dataArray does not exist")


    def test_init_not_dem_file(self):
        """dem_file not found or doesn't exist  
        """
        with self.assertRaises(FileNotFoundError) as err:

            Ecorrection(self.da_var[0], self.dem_file_wrong)

        self.assertEqual(err.exception.args[0], 'dem_file not found')


    def test_calculate_lapse_rate(self):
        """Tests Calculate_lapse_rate function
        """
        ecor = Ecorrection(self.da_var[0], self.dem_file)
        lapse_rate = ecor.calculate_lapse_rate(self.da_var[1], self.da_var[2])

        self.assertAlmostEqual(float(lapse_rate[162,72].values), -0.0017771)
        self.assertFalse(np.any(lapse_rate.values > 0.0294))
        self.assertFalse(np.any(lapse_rate.values < -0.0098))


    def test_lapse_rate_not_2t_dataarray(self):
        """Datarray without the desired variable (2t)
        """
        with self.assertRaises(ValueError) as err:

            ecor = Ecorrection(self.da_var[0], self.dem_file)
            ecor.calculate_lapse_rate(self.da_var[2], self.da_var[2])

        self.assertEqual(err.exception.args[0], '2t variable does not exist')


    def test_lapse_rate_not_orog_dataarray(self):
        """Datarray without the desired variable (orography)
        """
        with self.assertRaises(ValueError) as err:

            ecor = Ecorrection(self.da_var[0], self.dem_file)
            ecor.calculate_lapse_rate(self.da_var[1], self.da_var[1])

        self.assertEqual(err.exception.args[0], 'orography variable does not exist')

    def test_apply_correction(self):
        """Tests apply correction function
        """
        ecor = Ecorrection(self.da_var[0], self.dem_file)
        var_correction = ecor.apply_correction(self.dem_file, self.da_var[1], self.da_var[2])
        
        self.assertAlmostEqual(float(var_correction[162,72].values), 0.0500952)


    def test_apply_correction_lsm_true(self):
        """Tests apply correction function when lsm=True
        """
        ecor = Ecorrection(self.da_var[0], self.dem_file)
        var_correction = ecor.apply_correction(self.dem_file, self.da_var[1],
                                                self.da_var[2], landsea_mask=True)

        self.assertAlmostEqual(float(var_correction[1105,676].values), 9.6675980)

        
    def test_apply_correction_not_2t_dataarray(self):
        """Datarray without the desired variable (2t)
        """
        with self.assertRaises(ValueError) as err:

            ecor = Ecorrection(self.da_var[0], self.dem_file)
            ecor.apply_correction(self.dem_file, self.da_var[2],self.da_var[2])

        self.assertEqual(err.exception.args[0], '2t variable does not exist')


    def test_apply_correction_not_orog_dataarray(self):
        """Datarray without the desired variable (orography)
        """
        with self.assertRaises(ValueError) as err:

            ecor = Ecorrection(self.da_var[0], self.dem_file)
            ecor.apply_correction(self.dem_file, self.da_var[1], self.da_var[1])

        self.assertEqual(err.exception.args[0], 'orography variable does not exist')
