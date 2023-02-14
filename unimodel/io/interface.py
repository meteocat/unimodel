"""Interface for I/O grib readers.
"""
from unimodel.io.readers_nwp import (read_arome_grib, read_arpege_grib,
                                     read_bolam_grib, read_icon_grib,
                                     read_moloch_grib, read_wrf_prs)

_readers = dict()
_readers['arome'] = read_arome_grib
_readers['arpege'] = read_arpege_grib
_readers['bolam'] = read_bolam_grib
_readers['icon'] = read_icon_grib
_readers['moloch'] = read_moloch_grib
_readers['wrf'] = read_wrf_prs


def get_reader(name):
    """Returns a callable function for the reader method corresponding to
    the given name. The available options are 'arome', 'arpege', 'bolam',
    'icon', 'moloch' and 'wrf'.

    Args:
        name (str): Name of the NWP model.

    Raises:
        ValueError: If 'name' not in the available model list.

    Returns:
        function: NWP grib reader.
    """
    if isinstance(name, str):
        name = name.lower()

    try:
        reader_method = _readers[name]
        return reader_method
    except KeyError:
        raise ValueError(f"Unknown reader {name}\n The available readers are: "
                         + str(list(_readers.keys()))) from None
