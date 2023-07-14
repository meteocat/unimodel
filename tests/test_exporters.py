"""Tests exporters module.
"""
import pickle
import unittest

from unimodel.io.exporters import concat_and_merge


class TestExporters(unittest.TestCase):
    """Tests exporters module"""

    def test_concat_and_merge(self):
        """Test concat and merge a list of lists of models"""
        with open('tests/data/list_arome_xarray.pkl', 'rb') as file:
            arome_xarrays = pickle.load(file)
        with open('tests/data/list_bolam_xarray.pkl', 'rb') as file:
            bolam_xarrays = pickle.load(file)

        models_arrays = [arome_xarrays, bolam_xarrays]
        model_data = concat_and_merge(models_arrays)

        self.assertEqual(model_data.dims['x'], 620)
        self.assertEqual(model_data.dims['y'], 417)
        self.assertEqual(model_data.dims['valid_time'], 1)
        self.assertEqual(model_data.dims['model'], 2)

        self.assertEqual(model_data.valid_time.encoding['units'],
                         'hours since 2023-02-15 00:00:00')

        self.assertAlmostEqual(model_data.rio.transform().a,
                               0.010642497622783)
        self.assertAlmostEqual(model_data.rio.transform().b, 0.0)
        self.assertAlmostEqual(model_data.rio.transform().c,
                               -1.621137007661705)
        self.assertAlmostEqual(model_data.rio.transform().d, 0.0)
        self.assertAlmostEqual(model_data.rio.transform().e,
                               -0.010642497622783)
        self.assertAlmostEqual(model_data.rio.transform().f,
                               43.455589042260094)
