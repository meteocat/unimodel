"""Module to import NWP grib files.
"""
import tarfile
from datetime import datetime, timedelta
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

    # Valid datetime is required for ECMWF-HRES files
    valid_datetime = date_run + timedelta(hours=lead_time)
    if lead_time == 0:
        valid_datetime = valid_datetime.strftime('%m%d%H011')
    else:
        valid_datetime = valid_datetime.strftime('%m%d%H001')

    if config[model]['compressed']:
        # If model is informed as compressed (tar.gz), the key 'src_tar'
        # (tar source file) must be included in the configuration dictionary
        if 'src_tar' not in config[model].keys():
            raise KeyError('src_tar must be included if compressed is set to '
                           'True.')
        tar_file = config[model]['src_tar'].format(year=date_run_f['year'],
                                                   month=date_run_f['month'],
                                                   day=date_run_f['day'],
                                                   run=date_run_f['hour'])

        # If tar file is already copied in stage directory, program execution
        # continues
        if not exists(model_dir + basename(tar_file)):
            # If tar_file not exists, previous tar files are removed
            for prev_file in prev_files_tar:
                remove(prev_file)
            # If tar_file exists in source folder, it is copied to stage
            # directory
            if exists(tar_file):
                copy2(tar_file, model_dir)
            else:
                raise FileNotFoundError(tar_file + ' not found.')

    # NWP grib file is formatted following informed run date and lead time
    nwp_file = config[model]['src'].format_map({'year': date_run_f['year'],
                                                'month': date_run_f['month'],
                                                'day': date_run_f['day'],
                                                'hour': date_run_f['hour'],
                                                'run': date_run_f['hour'],
                                                'valid_time': valid_datetime,
                                                'lt': str(lead_time).zfill(2)})

    # If NWP grib file already exists in stage directory, this part is skipped
    if not exists(model_dir + basename(nwp_file)):
        # If NWP grib file not exists, previous grib files are removed
        for prev_file in prev_files:
            remove(prev_file)
        # If NWP grib file is from a compressed source, it is extracted
        if config[model]['compressed']:
            with tarfile.open(model_dir + basename(tar_file), 'r:gz') as _tar:
                for member in _tar:
                    _tar.makefile(member, model_dir + member.path)

        # Otherwise, if exists, it is directly copied to stage directory
        elif exists(nwp_file):
            copy2(nwp_file, model_dir)
        else:
            raise FileNotFoundError(nwp_file + ' not found.')

    return model_dir + basename(nwp_file)
