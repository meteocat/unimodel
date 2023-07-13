"""Tests load_config module.
"""
import unittest

from unimodel.utils.load_config import load_config


class TestLoadConfig(unittest.TestCase):
    """Tests load_config module"""
    def test_load_config(self):
        """Test loading of a config file"""
        config = load_config('tests/data/config_unimodel.json')

        self.assertEqual(config['lead_times'], 49)

    def test_load_config_not_found(self):
        """Test load_config when file not found"""
        with self.assertRaises(FileNotFoundError) as err:
            load_config('tests/data/not_found.json')

        self.assertEqual('tests/data/not_found.json does not exist.',
                         err.exception.args[0])
