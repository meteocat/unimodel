"""Module to test NWP importer module.
"""
import unittest
from datetime import datetime
from glob import glob
from shutil import rmtree
from copy import deepcopy
from os import makedirs, path

from unimodel.io.importers_nwp import import_nwp_grib


class TestNWPImporter(unittest.TestCase):
    """Tests function to import NWP grib files from filer to stage dir."""

    config = {
        "moloch_ecm": {
            "src_tar": "tests/data/nwp_src/moloch/"
            "moloch-grib2.{year}{month}{day}{run}"
            ".1p6.tar.gz",
            "src": "moloch-1p6-rep.{year}{month}{day}{run}_{lt}.grib2",
            "compressed": True,
            "lead_time_digits": 2,
        },
        "wrf43_prs": {
            "src": "tests/data/nwp_src/wrf43_prs/"
            "WRFPRS-03.{year}{month}{day}{run}_{lt}"
            ".grib",
            "compressed": False,
            "lead_time_digits": 3,
        },
        "wrf43_prs_tar": {
            "src": "tests/data/nwp_src/wrf43_prs/"
            "WRFPRS-03.{year}{month}{day}{run}_"
            "{lt}.grib",
            "lead_time_digits": 3,
            "compressed": True,
        },
        "ecmwf_hres": {
            "src": "tests/data/nwp_src/ecmwf_hres/A1S{month}"
            "{day}{run}00{valid_month}{valid_day}{valid_hour}1-99",
            "compressed": False,
        },
        "wrf_tl_ens": {
            "src_tar": "tests/data/nwp_src/wrf_tl_ens/"
            "NWCST_TL_ENS-membres.{year}{month}"
            "{day}{run}.tar.gz",
            "src": "ens-{member}.{year}{month}{day}{run}_{lt}.grib",
            "compressed": True,
            "lead_time_digits": 2,
        },
        "no_lt_digits": {
            "src": "tests/data/nwp_src/wrf43_prs/"
            "WRFPRS-03.{year}{month}{day}{run}_{lt}"
            ".grib",
            "compressed": False,
        },
        "wrf_gfs_3": {
            "src": "tests/data/nwp_src/wrf_gfs_3/WRFPRS_d01.{lt}",
            "compressed": False,
            "lead_time_digits": 3,
        },
        "nwp_dir": "tests/data/nwp_dir/",
    }

    def setUp(self) -> None:
        moloch_dir = "tests/data/nwp_dir/moloch_ecm"
        if path.isdir(moloch_dir):
            rmtree(moloch_dir)

        makedirs(moloch_dir)
        open("tests/data/nwp_dir/moloch_ecm/example.tar.gz", "wb")
        open("tests/data/nwp_dir/moloch_ecm/example.grib2", "wb")

        wrfprs_dir = "tests/data/nwp_dir/wrf43_prs"
        if path.isdir(wrfprs_dir):
            rmtree(wrfprs_dir)

        makedirs(wrfprs_dir)
        open("tests/data/nwp_dir/wrf43_prs/WRFPRS_d01.001", "wb")
        open("tests/data/nwp_dir/wrf43_prs/WRFPRS_d01.000", "wb")

        return super().setUp()

    def test_io_import_nwp_grib_compressed(self):
        """Tests import of a compressed grib file"""
        nwp_file = import_nwp_grib(
            datetime(2022, 11, 7, 0), 0, "moloch_ecm", self.config
        )

        self.assertEqual(
            nwp_file,
            "tests/data/nwp_dir/moloch_ecm/" "moloch-1p6-rep.2022110700_00.grib2",
        )

    def test_io_import_nwp_grib_compressed_tar_not_found(self):
        """Tests import of a compressed grib file"""
        with self.assertRaises(FileNotFoundError) as err:
            import_nwp_grib(datetime(2022, 11, 15, 0), 0, "moloch_ecm", self.config)

        self.assertEqual(
            err.exception.args[0],
            "tests/data/nwp_src/moloch/"
            "moloch-grib2.2022111500.1p6.tar.gz not found.",
        )

    def test_io_import_nwp_grib_compressed_src_not_found(self):
        """Tests import of a compressed grib file"""
        with self.assertRaises(FileNotFoundError) as err:
            import_nwp_grib(datetime(2022, 11, 7, 0), 200, "moloch_ecm", self.config)

        self.assertEqual(
            err.exception.args[0],
            "moloch-1p6-rep.2022110700_200.grib2 not found in "
            "tests/data/nwp_src/moloch/"
            "moloch-grib2.2022110700.1p6.tar.gz.",
        )

    def test_io_import_nwp_grib_not_compressed(self):
        """Tests import of a not compressed grib file"""
        nwp_file = import_nwp_grib(
            datetime(2023, 2, 6, 0), 32, "wrf43_prs", self.config
        )

        self.assertEqual(
            nwp_file, "tests/data/nwp_dir/wrf43_prs/" "WRFPRS-03.2023020600_032.grib"
        )

    def test_io_import_nwp_grib_not_compressed_not_found(self):
        """Tests import of a compressed grib file"""
        with self.assertRaises(FileNotFoundError) as err:
            import_nwp_grib(datetime(2022, 11, 15, 0), 0, "wrf43_prs", self.config)

        self.assertEqual(
            err.exception.args[0],
            "tests/data/nwp_src/wrf43_prs/" "WRFPRS-03.2022111500_000.grib not found.",
        )

    def test_io_import_nwp_grib_model_not_in_config(self):
        """Tests import of a model not in configuration dictionary"""
        with self.assertRaises(KeyError) as err:
            import_nwp_grib(datetime(2022, 11, 7, 0), 2, "molcho", self.config)

        self.assertEqual(
            err.exception.args[0], "molcho not in configuration dictionary."
        )

    def test_io_import_nwp_grib_model_not_src_tar(self):
        """Tests import of a comprsessed model without src_tar"""
        with self.assertRaises(KeyError) as err:
            import_nwp_grib(datetime(2022, 11, 7, 0), 2, "wrf43_prs_tar", self.config)

        self.assertEqual(
            err.exception.args[0],
            "src_tar must be included if " "compressed is set to True.",
        )

    def test_io_import_nwp_grib_ecmwf_lt_0(self):
        """Tests import of a ECMWF-HRES grib file corresponding to lt=0"""
        nwp_file = import_nwp_grib(
            datetime(2023, 2, 20, 0), 0, "ecmwf_hres", self.config
        )

        self.assertEqual(
            nwp_file, "tests/data/nwp_dir/ecmwf_hres/" "A1S02200000022000011-99"
        )

    def test_io_import_nwp_grib_ecmwf_lt_not_0(self):
        """Tests import of a ECMWF-HRES grib file corresponding to lt!=0"""
        nwp_file = import_nwp_grib(
            datetime(2023, 2, 20, 0), 6, "ecmwf_hres", self.config
        )

        self.assertEqual(
            nwp_file, "tests/data/nwp_dir/ecmwf_hres/" "A1S02200000022006001-99"
        )

    def test_io_import_nwp_tl_ens_grib_compressed(self):
        """Tests import of a compressed grib file"""
        nwp_file = import_nwp_grib(
            datetime(2023, 3, 20, 9), 1, "wrf_tl_ens", self.config
        )

        self.assertEqual(
            sorted(nwp_file)[0],
            "tests/data/nwp_dir/wrf_tl_ens/" "ens-001.2023032009_01.grib",
        )
        self.assertEqual(len(nwp_file), 12)

        # Double test to check re-use of already extracted files from a .tar.gz
        nwp_file = import_nwp_grib(
            datetime(2023, 3, 20, 9), 4, "wrf_tl_ens", self.config
        )

        self.assertEqual(
            sorted(nwp_file)[0],
            "tests/data/nwp_dir/wrf_tl_ens/" "ens-001.2023032009_04.grib",
        )
        self.assertEqual(len(nwp_file), 12)

    def test_io_import_nwp_grib_model_not_lt_digits(self):
        """Tests import of a comprsessed model without src_tar"""
        with self.assertRaises(KeyError) as err:
            import_nwp_grib(datetime(2022, 11, 7, 0), 2, "no_lt_digits", self.config)

        self.assertEqual(
            err.exception.args[0],
            "If named argument {lt} in "
            "'src', then 'lead_time_digits' must be "
            "specified.",
        )

    def test_io_import_nwp_conflicting_lead_times(self):
        """Tests importing files with conflicting lead times
        (ex 12 and 120)"""
        nwp_file = import_nwp_grib(
            datetime(2022, 11, 19, 0), 12, "wrf_gfs_3", self.config
        )
        self.assertTrue(isinstance(nwp_file, str))
        self.assertNotEqual(nwp_file, "tests/data/nwp_dir/WRFPRS_d01.120")

    # def test_io_import_nwp_file_not_in_tar(self):
    #     """Tests importing files with conflicting lead times
    #     (ex 12 and 120)"""
    #     modified_config = deepcopy(self.config)
    #     modified_config['moloch_ecm']['src'] = 'wrong_file_name'

    #     nwp_file = import_nwp_grib(
    #         datetime(2022, 11, 7, 0), 0, "moloch_ecm", modified_config
    #     )
    #     self.assertTrue(isinstance(nwp_file, str))
    #     self.assertNotEqual(nwp_file, "tests/data/nwp_dir/WRFPRS_d01.120")

    def tearDown(self) -> None:
        for f_dir in glob(self.config["nwp_dir"] + "/*"):
            rmtree(f_dir)
        return super().tearDown()
