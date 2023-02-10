"""Module to import NWP grib files.
"""
import tarfile
from datetime import datetime
from glob import glob
from os import makedirs, remove
from posixpath import basename
from shutil import copy2

from genericpath import exists


def _get_datetime_formatted(date: datetime) -> dict:
    year = date.strftime('%Y')
    month = date.strftime('%m')
    day = date.strftime('%d')
    hour = date.strftime('%H')
    minute = date.strftime('%M')
    second = date.strftime('%S')

    return {'year': year, 'month': month, 'day': day, 'hour': hour,
            'minute': minute, 'second': second}


def import_nwp_grib(date_run: datetime, lead_time: int, model: str,
                    config: dict) -> str:
    """Copies NWP grib files from a source directory to a stage directory.

    Args:
        date_run (datetime): Datetime of the model run.
        lead_time (int): Lead time of the forecast to extract.
        model (str): Name of the model
        config (dict): Configuration dictionary.

    Raises:
        KeyError: If 'model' not in the configuration dictionary.
        KeyError: If 'src_tar' not included when 'compressed' set to True.'
        FileNotFoundError: If source tar file not found.
        FileNotFoundError: If source grib file not found.

    Returns:
        str: Path to the grib file.
    """
    if model not in config.keys():
        raise KeyError(model + ' not in configuration dictionary.')

    model_dir = config['nwp_dir'] + model + '/'
    if not exists(model_dir):
        makedirs(model_dir)

    prev_files_tar = glob(model_dir + '*.tar.gz')
    prev_files = glob(model_dir + '*[!.tar.gz]')

    date_run_f = _get_datetime_formatted(date_run)

    if config[model]['compressed']:
        if 'src_tar' not in config[model].keys():
            raise KeyError('src_tar must be included if compressed is set to '
                           'True.')
        tar_file = config[model]['src_tar'].format(year=date_run_f['year'],
                                                   month=date_run_f['month'],
                                                   day=date_run_f['day'],
                                                   run=date_run_f['hour'])

        if not exists(model_dir + basename(tar_file)):
            for prev_file in prev_files_tar:
                remove(prev_file)
            if exists(tar_file):
                copy2(tar_file, model_dir)
            else:
                raise FileNotFoundError(tar_file + ' not found.')

    nwp_file = config[model]['src'].format_map({'year': date_run_f['year'],
                                                'month': date_run_f['month'],
                                                'day': date_run_f['day'],
                                                'hour': date_run_f['hour'],
                                                'run': date_run_f['hour'],
                                                'lt': str(lead_time).zfill(2)})

    if not exists(model_dir + basename(nwp_file)):
        for prev_file in prev_files:
            remove(prev_file)
        if config[model]['compressed']:
            with tarfile.open(model_dir + basename(tar_file)) as tar:
                tar.extract(nwp_file, path=model_dir)
        elif exists(nwp_file):
            copy2(nwp_file, model_dir)
        else:
            raise FileNotFoundError(nwp_file + ' not found.')

    return model_dir + basename(nwp_file)
