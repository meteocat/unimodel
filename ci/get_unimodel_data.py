"""Script to download Unimodel test data for CI purposes.
"""
import os

from unimodel.utils.unimodel_data import download_unimodel_test_data

test_dir = os.environ['UNIMODEL_DATA_PATH']

download_unimodel_test_data(test_dir)
