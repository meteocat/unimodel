"""Tests interface for I/O methods.
"""
import unittest
import unimodel.io
from unimodel.io.readers_nwp import (read_arome_grib, read_arpege_grib,
                                     read_bolam_grib, read_icon_grib,
                                     read_moloch_grib, read_wrf_prs)


class TestIOInterface(unittest.TestCase):
    """Tests the io interface"""
    def test_io_interface(self):
        """Test the io module interface."""
        reader_pairs = [("arome", read_arome_grib),
                        ("arpege", read_arpege_grib),
                        ("bolam", read_bolam_grib),
                        ("icon", read_icon_grib),
                        ("moloch_ecm", read_moloch_grib),
                        ("moloch_gfs", read_moloch_grib),
                        ("wrf_exp", read_wrf_prs)]

        for reader_pair in reader_pairs:
            reader_method = unimodel.io.get_reader(reader_pair[0])
            self.assertEqual(reader_method, reader_pair[1])

        with self.assertRaises(ValueError) as err:
            unimodel.io.get_reader('noaa')

        self.assertEqual(err.exception.args[0], 'Unknown reader noaa\n '
                         'The available readers are: [\'arome\', \'arpege\', '
                         '\'bolam\', \'icon\', \'moloch_gfs\', \'moloch_ecm\','
                         ' \'wrf_ecm\', \'wrf_exp\', \'wrf_gfs_3\', '
                         '\'wrf_gfs_9\', \'ecmwf_hres\']')
