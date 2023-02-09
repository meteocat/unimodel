"""Module to read NWP files and transfrom them to xarray.
"""
import numpy as np
import pyproj
import xarray
from rasterio import Affine

from unimodel.utils.geotools import proj4_from_grib


def _get_wrf_prs_metadata(xarray_var: xarray.DataArray) -> dict:
    """Get projection, Affine transform and shape from a PRS xarray.

    Args:
        xarray_var (xarray): xarray to get information from.

    Returns:
        dict: CRS, x size, y size and Affine transform.
    """
    dx = xarray_var.attrs['GRIB_DxInMetres']
    dy = xarray_var.attrs['GRIB_DyInMetres']
    nx = xarray_var.attrs['GRIB_Nx']
    ny = xarray_var.attrs['GRIB_Ny']

    crs_wrf = pyproj.CRS(
        '+proj=lcc +units=m +R=6370000'
        ' +lat_1=' + str(xarray_var.attrs['GRIB_Latin2InDegrees']) +
        ' +lat_2=' + str(xarray_var.attrs['GRIB_Latin1InDegrees']) +
        # ' +lat_0=' + str(xarray_var.attrs['GRIB_LaDInDegrees']) +
        ' +lat_0=40.70002' +
        ' +lon_0=' + str(xarray_var.attrs['GRIB_LoVInDegrees']) +
        ' +nadgrids=@null')
    crs_gcp = pyproj.CRS('EPSG:4326')

    # Easting and Northings of the domains center point
    transformer = pyproj.Transformer.from_crs(crs_gcp, crs_wrf)

    # Up left corner of domain
    x0, y0 = transformer.transform(
        float(xarray_var.attrs['GRIB_latitudeOfFirstGridPointInDegrees']),
        float(xarray_var.attrs['GRIB_longitudeOfFirstGridPointInDegrees']))
    y0 = (ny-1) * dy + y0

    # Wrfout geotransform
    wrfout_gt = (-252466.8378711785+1500, 3000.0, 0.0,
                 391438.10408251436-1500, 0.0, -3000.0)

    return {'affine': Affine.from_gdal(wrfout_gt[0], wrfout_gt[1],
                                       wrfout_gt[2], wrfout_gt[3],
                                       wrfout_gt[4], wrfout_gt[5]),
            # 'affine': Affine.from_gdal(x0, dx, 0, y0, 0, -dy),
            'crs': crs_wrf, 'x_size': nx, 'y_size': ny}


def read_wrf_prs(grib_file: str, variable: str) -> xarray.DataArray:
    """Reads a WRF grib file and transforms it into an xarray.DataArray.

    Args:
        grib_file (string): Path to a WRF grib file.
        variable (string): Variable to extract.
    Returns:
        xarray: Contains the data and the geographical information to
                transform the grids
    """
    grib_data = xarray.open_dataarray(grib_file, engine='cfgrib',
                backend_kwargs=dict(filter_by_keys={'shortName': variable}))

    geographics = _get_wrf_prs_metadata(grib_data)
    grib_data = grib_data.rio.write_crs(geographics['crs'])
    grib_data.rio.write_transform(geographics['affine'], inplace=True)

    return grib_data


def read_moloch_grib(grib_file: str, variable: str) -> xarray.DataArray:
    """Reads a Moloch grib file and transforms it into an xarray.DataArray.

    Args:
        grib_file (str): Path to a Moloch grib file.
        variable (str): Variable to extract.

    Returns:
        xarray: Moloch grib file data.
    """
    grib_filter = {'shortName': variable}

    grib_data = xarray.open_dataarray(grib_file, engine='cfgrib',
                    backend_kwargs=dict(filter_by_keys=grib_filter))

    grib_md = _get_moloch_metadata(grib_data)

    grib_data.rio.write_crs(grib_md['crs'], inplace=True)

    x_coords = np.linspace(grib_md['x0'],
                           grib_md['x0'] + (grib_md['x_size'] * grib_md['dx'])
                           - grib_md['dx'],
                           grib_md['x_size'])

    y_coords = np.linspace(grib_md['y0'],
                           grib_md['y0'] + (grib_md['y_size'] * grib_md['dy'])
                           - grib_md['dy'],
                           grib_md['y_size'])

    grib_data = grib_data.assign_coords(x=x_coords, y=y_coords)
    grib_data.rio.write_crs(grib_md['crs'], inplace=True)
    grib_data = grib_data.drop_vars(['latitude', 'longitude'], errors='ignore')

    return grib_data


def _get_moloch_metadata(moloch_data: xarray.DataArray) -> dict:

    moloch_projection = proj4_from_grib(moloch_data)

    x_0 = moloch_data.attrs['GRIB_longitudeOfFirstGridPointInDegrees']
    d_x = moloch_data.attrs['GRIB_iDirectionIncrementInDegrees']

    y_0 = moloch_data.attrs['GRIB_latitudeOfFirstGridPointInDegrees']
    d_y = moloch_data.attrs['GRIB_jDirectionIncrementInDegrees']

    return {'x0': x_0, 'dx': d_x, 'y0': y_0, 'dy': d_y,
            'crs': moloch_projection,
            'x_size': moloch_data.attrs['GRIB_Nx'],
            'y_size': moloch_data.attrs['GRIB_Ny']}


def read_bolam_grib(grib_file: str, variable: str) -> xarray.DataArray:
    """Reads a Bolam grib file and transforms it into an xarray.DataArray.

    Args:
        grib_file (str): Path to a Bolam grib file.
        variable (str): Variable to extract.

    Returns:
        xarray: Bolam grib file data.
    """
    grib_filter = {'shortName': variable}

    grib_data = xarray.open_dataarray(grib_file, engine='cfgrib',
                    backend_kwargs=dict(filter_by_keys=grib_filter))

    grib_md = _get_bolam_metadata(grib_data)

    grib_data.rio.write_crs(grib_md['crs'], inplace=True)

    x_coords = np.linspace(grib_md['x0'],
                           grib_md['x0'] + (grib_md['x_size'] * grib_md['dx'])
                           - grib_md['dx'],
                           grib_md['x_size'])

    y_coords = np.linspace(grib_md['y0'],
                           grib_md['y0'] + (grib_md['y_size'] * grib_md['dy'])
                           - grib_md['dy'],
                           grib_md['y_size'])

    grib_data = grib_data.assign_coords(x=x_coords, y=y_coords)
    grib_data.rio.write_crs(grib_md['crs'], inplace=True)
    grib_data = grib_data.drop_vars(['latitude', 'longitude'], errors='ignore')

    return grib_data


def _get_bolam_metadata(bolam_data: xarray.DataArray) -> dict:

    bolam_projection = proj4_from_grib(bolam_data)

    x_0 = bolam_data.attrs['GRIB_longitudeOfFirstGridPointInDegrees'] - 360.0
    d_x = bolam_data.attrs['GRIB_iDirectionIncrementInDegrees']

    y_0 = bolam_data.attrs['GRIB_latitudeOfFirstGridPointInDegrees']
    d_y = bolam_data.attrs['GRIB_jDirectionIncrementInDegrees']

    return {'x0': x_0, 'dx': d_x, 'y0': y_0, 'dy': d_y,
            'crs': bolam_projection,
            'x_size': bolam_data.attrs['GRIB_Nx'],
            'y_size': bolam_data.attrs['GRIB_Ny']}
