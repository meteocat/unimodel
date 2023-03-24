
import xarray as xr
from datetime import timedelta, datetime

import numpy as np

from dateutil.rrule import rrule, HOURLY


def pad_xarray(data, lead_times):
    print(data)
    if len(data.time.shape)==0:
        data_ini = datetime.utcfromtimestamp(data.time.values.astype(datetime)/1e9)
        data_ini_pad = data_ini + timedelta(hours=1) 
        data_fi_pad = data_ini + timedelta(hours=lead_times)
        data= data.expand_dims(dim={'time':[data_ini]})
    else:
        data_ini_pad = datetime.utcfromtimestamp(data.time.valuesastype(datetime).tolist()/1e9)[-1]
        data_ini_pad = data_ini_pad + timedelta(hours=1) 
        data_ini = datetime.utcfromtimestamp(data.time.valuesastype(datetime).tolist()/1e9)[0]
        data_fi_pad = data_ini + timedelta(hours=lead_times)

    num_pad=int((data_fi_pad - data_ini_pad).days*24+(data_fi_pad - data_ini_pad).seconds/3600)+1

    slice_time = list(rrule(HOURLY, dtstart=data_ini, until=data_fi_pad))
    
    data = data.pad(time=(0,num_pad), constant_values=np.nan)
    data.assign_coords({'time':slice_time})
    data = data.assign_coords({'time':slice_time})
    return data

