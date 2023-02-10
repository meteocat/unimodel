"""Module to test NWP importer module.
"""
import unittest
from datetime import datetime
from glob import glob
from shutil import rmtree

from unimodel.io.importers_nwp import import_nwp_grib


class TestNWPImporter(unittest.TestCase):
    """Tests function to import NWP grib files from filer to stage dir.
    """
    config = {'moloch_ecm': {'src_tar': 'tests/data/nwp_src/moloch/'
                                        'moloch-grib2.{year}{month}{day}{run}'
                                        '.1p6.tar.gz',
                             'src': 'moloch-1p6-rep.{year}{month}{day}{run}'
                                    '_{lt}.grib2',
                             'compressed': True},
              'wrf43_prs': {'src': 'tests/data/nwp_src/wrf43_prs/'
                                  'WRFPRS-03.{year}{month}{day}{run}_0{lt}'
                                  '.grib',
                            'compressed': False},
              'nwp_dir': 'tests/data/nwp_dir/'}


    def test_io_import_nwp_grib_compressed(self):
        """Tests import of a compressed grib file."""
        nwp_file = import_nwp_grib(datetime(2022, 11, 7, 0), 0, 'moloch_ecm',
                                   self.config)

        self.assertEqual(nwp_file, 'tests/data/nwp_dir/moloch_ecm/'
                         'moloch-1p6-rep.2022110700_00.grib2')

    def test_io_import_nwp_grib_not_compressed(self):
        """Tests import of a not compressed grib file."""
        nwp_file = import_nwp_grib(datetime(2023, 2, 6, 0), 32, 'wrf43_prs',
                                   self.config)

        self.assertEqual(nwp_file, 'tests/data/nwp_dir/wrf43_prs/'
                         'WRFPRS-03.2023020600_032.grib')

    def test_io_import_nwp_grib_model_not_in_config(self):
        """Tests import of a model not in configuration dictionary."""
        with self.assertRaises(KeyError) as cm:
            import_nwp_grib(datetime(2022, 11, 7, 0), 2, 'molcho', self.config)

        self.assertEqual(cm.exception.args[0],
                         'molcho not in configuration dictionary.')

    def tearDown(self) -> None:
        for f_dir in glob(self.config['nwp_dir'] + '/*'):
            rmtree(f_dir)
        return super().tearDown()
