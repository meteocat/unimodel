"""Unimodel decorators.
"""
import xarray


def xarray_attributes(func):
    '''Measure performance of a function'''

    def check_attributes(*args, **kwargs):

        xarray_data = func(*args, **kwargs)

        # Borrem els atributs GRIB que no necessitem
        for attribute in list(xarray_data.attrs):
            if 'GRIB' in attribute:
                del xarray_data.attrs[attribute]

        if isinstance(xarray_data, xarray.DataArray):
            if 'model' in xarray_data.dims:
                if len(xarray_data.model.data) > 1:
                    del xarray_data.attrs['model']
                    xarray_data.attrs['models'] = list(xarray_data.model.data)

        if isinstance(xarray_data, xarray.Dataset):
            if xarray_data.dims.get('model') > 1:
                del xarray_data.attrs['model']
                xarray_data.attrs['models'] = list(xarray_data.model.data)

        return xarray_data

    return check_attributes
