from urllib import request
from zipfile import ZipFile
import os
from shutil import copytree, rmtree
from tempfile import TemporaryDirectory


def download_unimodel_test_data(test_dir: str) -> None:
    """Download unimodel data from github.

    Args:
        test_dir (str): Directory where Unimodel test data will be saved.
    """
    if os.path.exists(test_dir):
        rmtree(test_dir)

    file_name, _ = request.urlretrieve(
        'https://github.com/meteocat/unimodel-data/archive/refs/heads/'
        'main.zip')

    with ZipFile(file_name, 'r') as zip_obj:
        tmp_dir = TemporaryDirectory()
        common_path = os.path.commonprefix(zip_obj.namelist())
        zip_obj.extractall(tmp_dir.name)

        copytree(os.path.join(tmp_dir.name, common_path), test_dir)
