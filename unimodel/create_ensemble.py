import unimodel.io
from datetime import datetime
from unimodel.io.importers_nwp import import_nwp_grib
from unimodel.downscaling.interpolation import bilinear
from unimodel.io.exporters import export_to_netcdf
from unimodel.utils.load_config import load_config


# Definim variables a partir del fitxer de configuracio
# config = load_config(ARGS.config)
config = load_config('config_unimodel.json')

models = ['moloch_ecm', 'arome']
date = datetime(2023, 2, 22)
list_out_models=[]
for model in models:
    time_0 = datetime.utcnow()
    print(model)
    out_model = []
    for lt in range(config['lead_times']):
        print(lt)
        nwp_file = import_nwp_grib(date, lt, model, config)
        reader = unimodel.io.get_reader(model)
        nwp_data = reader(nwp_file, 'tp', model)
        rep_data = bilinear(nwp_data, config['corner_ul'],
                            config['grid_shape'], config['grid_res'],
                            'epsg:4326')
        out_model.append(rep_data)
    list_out_models.append(out_model)
    time_1 = datetime.utcnow()
    print((time_1 - time_0).total_seconds() / 60)

export_to_netcdf(list_out_models, config['netcdf_output'])

print(nwp_file)