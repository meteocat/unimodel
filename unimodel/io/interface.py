# -*- coding: utf-8 -*-
"""
pysteps.motion.interface
========================
Interface for the motion module. It returns a callable optical flow routine for
computing the motion field.
The methods in the motion module implement the following interface:
    ``motion_method(precip, **keywords)``
where precip is a (T,m,n) array containing a sequence of T two-dimensional input
images of shape (m,n). The first dimension represents the images time dimension
and the value of T depends on the type of the method.
The output is a three-dimensional array (2,m,n) containing the dense x- and
y-components of the motion field in units of pixels / timestep as given by the
input array R.
.. autosummary::
    :toctree: ../generated/
    get_method
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
    """
    Return a callable function for the reader method corresponding to
    the given name. The available options are 'arome', 'arpege', 'bolam',
    'icon', 'moloch' and 'wrf'.
    """
    if isinstance(name, str):
        name = name.lower()

    try:
        reader_method = _readers[name]
        return reader_method
    except KeyError:
        raise ValueError(
            f"Unknown reader {name}\n The available readers are: "
            + str(list(_readers.keys()))
        ) from None
