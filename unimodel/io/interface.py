"""Interface for I/O grib readers."""

from unimodel.io.readers_nwp import (
    read_arome_grib,
    read_arpege_grib,
    read_bolam_grib,
    read_ecmwf_grib,
    read_icon_grib,
    read_moloch_grib,
    read_unified_model_grib,
    read_wrf_prs,
    read_wrf_tl_ens_grib,
    read_ncep_grib,
    read_swan_grib,
    read_ww3_grib,
)

_readers = dict()
_readers["arome"] = read_arome_grib
_readers["arpege"] = read_arpege_grib
_readers["bolam"] = read_bolam_grib
_readers["icon"] = read_icon_grib
_readers["moloch_gfs"] = read_moloch_grib
_readers["moloch_ecm"] = read_moloch_grib
_readers["wrf_ecm"] = read_wrf_prs
_readers["wrf_exp"] = read_wrf_prs
_readers["wrf_gfs_3"] = read_wrf_prs
_readers["wrf_gfs_9"] = read_wrf_prs
_readers["ecmwf"] = read_ecmwf_grib
_readers["ecmwf_hres"] = read_ecmwf_grib
_readers["ecmwf_ens"] = read_ecmwf_grib
_readers["unified_model"] = read_unified_model_grib
_readers["wrf_tl_ens"] = read_wrf_tl_ens_grib
_readers["gfs"] = read_ncep_grib
_readers["gefs"] = read_ncep_grib
_readers["swan"] = read_swan_grib
_readers["ww3"] = read_ww3_grib


def get_reader(name):
    """Returns a callable function for the reader method corresponding to
    the given name. The available options are 'arome', 'arpege', 'bolam',
    'icon', 'moloch_gfs', 'moloch_ecm', 'wrf_ecm', 'wrf_exp', 'wrf_gfs_3',
    'wrf_gfs_9', 'ecmwf', 'ecmwf_hres', 'ecmwf_ens', 'wrf_tl_ens' and 'unified_model'.

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
        raise ValueError(
            f"Unknown reader {name}\n The available readers are: "
            + str(list(_readers.keys()))
        ) from None
