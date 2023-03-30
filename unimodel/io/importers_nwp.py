"""Module to import NWP grib files.
"""
import tarfile
from datetime import datetime, timedelta
from glob import glob
from os import makedirs, remove
from posixpath import basename
from shutil import copy2
import re

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

    if r'{lt}' in config[model]['src']:
        if 'lead_time_digits' not in config[model].keys():
            raise KeyError('If named argument {lt} in \'src\', then '
                           '\'lead_time_digits\' must be specified.')
        lt_digits = config[model]['lead_time_digits']
    else:
        lt_digits = 0

    # NWP grib file is formatted following informed run date and lead time.
    # Regular expression [0-9]* (it matches a single character in the range
    # between 0 and 9 unlimited times) is assigned to 'member' named arguments
    # since WRF-TL-ENS paths include the number of the ensemble member.
    nwp_file = config[model]['src'].format_map(
        {'year': date_run_f['year'], 'month': date_run_f['month'],
         'day': date_run_f['day'], 'hour': date_run_f['hour'],
         'run': date_run_f['hour'], 'valid_time': valid_datetime,
         'lt': str(lead_time).zfill(lt_digits), 'member': r"[0-9]*"})

    # Checks if NWP grib files already exist in stage directory. If exist, path
    # is appended to nwp_files list.
    nwp_files = []
    for prev_file in prev_files:
        if re.match(model_dir + basename(nwp_file), prev_file):
            nwp_files.append(prev_file)

    # If the previous list is empty, files must be copied from source or
    # .tar.gz file
    if len(nwp_files) == 0:
        # If NWP grib file not exists, previous grib files are removed
        for prev_file in prev_files:
            remove(prev_file)
        # If NWP grib file is from a compressed source, it is extracted
        if config[model]['compressed']:
            with tarfile.open(model_dir + basename(tar_file), 'r:gz') as _tar:
                for member in _tar:
                    _tar.makefile(member, model_dir + member.path)
                    if bool(re.match(basename(nwp_file), member.path)):
                        nwp_files.append(model_dir + member.path)

        # Otherwise, if exists, it is directly copied to stage directory
        elif exists(nwp_file):
            copy2(nwp_file, model_dir)
            nwp_files.append(model_dir + basename(nwp_file))
        else:
            raise FileNotFoundError(nwp_file + ' not found.')

    if len(nwp_files) > 1:
        return nwp_files

    return nwp_files[0]
