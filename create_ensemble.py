"""Main script to create an ensemble from different NWP model gribs.
"""
from datetime import datetime

import dask

import unimodel.io
from unimodel.downscaling.interpolation import bilinear
from unimodel.io.exporters import export_to_netcdf
from unimodel.io.importers_nwp import import_nwp_grib
from unimodel.utils.load_config import load_config


def __process_model(model, date, config):
    """Processes and interpolates each model to a common grid.

    Args:
        model (str): NWP model name.
        date (datetime): Run date of NWP model.
        config (dict): Configuration dictionary

    Returns:
        list: xarray including all lead times of NWP model run.
    """
    out_model = []
    for lead_time in range(config['lead_times']):
        nwp_file = import_nwp_grib(date, lead_time, model, config)
        reader = unimodel.io.get_reader(model)
        nwp_data = reader(nwp_file, 'tp', model)
        rep_data = bilinear(nwp_data, config['corner_ul'],
                            config['grid_shape'], config['grid_res'],
                            'epsg:4326')
        out_model.append(rep_data)

    return out_model


def main():
    """Creates an ensemble from different NWP model grib files.
    """
    # Definim variables a partir del fitxer de configuracio
    # config = load_config(ARGS.config)
    config = load_config('config_unimodel.json')

    models = ['wrf_gfs_9', 'wrf_gfs_3', 'wrf_exp', 'wrf_ecm',
              'moloch_ecm', 'moloch_gfs', 'ecmwf_hres', 'arome',
              'bolam', 'icon', 'arpege']

    models = ['moloch_ecm']

    date = datetime(2023, 2, 24)

    time_total_0 = datetime.utcnow()
    lazy_results = []
    for model in models:
        lazy_result = dask.delayed(__process_model)(model, date, config)
        lazy_results.append(lazy_result)

    processed = dask.compute(*lazy_results)

    export_to_netcdf(processed, config['netcdf_output'])

    time_total_1 = datetime.utcnow()
    print((time_total_1 - time_total_0).total_seconds() / 60)


if __name__ == '__main__':

    main()
