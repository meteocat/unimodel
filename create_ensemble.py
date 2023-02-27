import unimodel.io
from datetime import datetime
from unimodel.io.importers_nwp import import_nwp_grib
from unimodel.downscaling.interpolation import bilinear
from unimodel.io.exporters import export_to_netcdf
from unimodel.utils.load_config import load_config
import dask


def process_model(model, date, config):
    out_model = []
    for lt in range(config['lead_times']):
        nwp_file = import_nwp_grib(date, lt, model, config)
        reader = unimodel.io.get_reader(model)
        nwp_data = reader(nwp_file, 'tp', model)
        rep_data = bilinear(nwp_data, config['corner_ul'],
                            config['grid_shape'], config['grid_res'],
                            'epsg:4326')
        out_model.append(rep_data)
    
    return out_model

# Definim variables a partir del fitxer de configuracio
# config = load_config(ARGS.config)
config = load_config('config_unimodel.json')

models = ['moloch_ecm', 'moloch_gfs', 'bolam', 'ecmwf_hres', 'icon', 'arpege',
          'arome', 'wrf_gfs_9', 'wrf_gfs_3', 'wrf_exp', 'wrf_ecm']

models = ['wrf_gfs_9', 'wrf_gfs_3', 'wrf_exp', 'wrf_ecm',
          'moloch_ecm', 'moloch_gfs', 'ecmwf_hres', 'arome',
          'bolam', 'icon', 'arpege']

date = datetime(2023, 2, 24)
list_out_models=[]

time_total_0 = datetime.utcnow()
lazy_results = []
for model in models:
    lazy_result = dask.delayed(process_model)(model, date, config)
    lazy_results.append(lazy_result)

processed = dask.compute(*lazy_results)

export_to_netcdf(processed, config['netcdf_output'])


time_total_1 = datetime.utcnow()
print((time_total_1 - time_total_0).total_seconds() / 60)