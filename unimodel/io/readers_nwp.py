"""Module to read NWP files and transfrom them to xarray.
"""
import numpy as np
import pyproj
import xarray

from unimodel.utils.geotools import proj4_from_grib


def read_wrf_prs(grib_file: str, variable: str) -> xarray.DataArray:
    """Reads a WRF grib file and transforms it into an xarray.DataArray.

    Args:
        grib_file (string): Path to a WRF grib file.
        variable (string): Variable to extract.

    Returns:
        xarray: WRF PRS grib file data.
    """
    grib_data = xarray.open_dataarray(grib_file, engine='cfgrib',
                    backend_kwargs={'filter_by_keys': {'shortName': variable}})
    geographics = _get_wrf_prs_metadata(grib_data)
    grib_data = grib_data.rio.write_crs(geographics['crs'])

    # WRF PRS xarray does not have coordinates in its projection (Lambert),
    # only the equivalent irregulat longitude and latitude points. Then, x and
    # y coordinates must be created following the metadata obtained in
    # _get_wrf_prs_metedata.
    x_coords = np.linspace(geographics['x0'],
                           geographics['x0'] + ((geographics['x_size'] -1) *
                           geographics['dx']),
                           geographics['x_size'])

    y_coords = np.linspace(geographics['y0'],
                           geographics['y0'] + ((geographics['y_size'] -1)*
                           geographics['dy']),
                           geographics['y_size'])
    y_coords = y_coords[::-1]

    grib_data = grib_data.assign_coords(x=x_coords, y=y_coords)
    grib_data = grib_data.drop_vars(['latitude', 'longitude'], errors='ignore')

    return grib_data


def _get_wrf_prs_metadata(xarray_var: xarray.DataArray) -> dict:
    """Get projection, Affine transform and shape from a PRS xarray.

    Args:
        xarray_var (xarray): xarray to get information from.

    Returns:
        dict: CRS, x size, y size and Affine transform.
    """
    d_x = xarray_var.attrs['GRIB_DxInMetres']
    d_y = xarray_var.attrs['GRIB_DyInMetres']
    n_x = xarray_var.attrs['GRIB_Nx']
    n_y = xarray_var.attrs['GRIB_Ny']

    # WRF PRS projection lat_0 is not correctly defined in the file.
    # Then, it must be updated to 40.70002. Therefore, we harcoded all WRF PRS
    # projection.
    crs_wrf = pyproj.CRS('+proj=lcc +units=m +R=6370000 +lat_1=60.0 '
                         '+lat_2=30.0 +lat_0=40.70002 +lon_0=-1.5 '
                         '+nadgrids=@null')

    # WRF PRS is a GRIB1 file and does not provide enough precision for corner
    # coordinates. Then, geotransform must be calculated following alternative
    # approaches. The most appropriate can be found in
    # https://meteocat.atlassian.net/wiki/spaces/RAM/pages/
    #        2820702244/Geotransform+WRF
    # The obtained geotransform corresponds to:
    #
    #   (-252466.8378711785, 3000.0, 0.0, 391438.10408251436, 0.0, -3000.0)
    #
    # Then, the upper left corner is:
    x_0 = -252466.8378711785
    y_0 = 391438.10408251436

    # Since geotransform provides pixel corner coordinates, we must obtain the
    # center pixel coordinates
    x_0 = x_0 + d_x/2
    y_0 = y_0 - d_y/2

    # d_y must be decreasing
    return {'x0': x_0, 'y0': y_0, 'dx': d_x, 'dy': -d_y, 'crs': crs_wrf,
            'x_size': n_x, 'y_size': n_y}


def read_icon_grib(file, variable):
    """Read wrf variable chosen in a ICON grib file

    Args:
        grib_file (string): Path to a WRF grib file.
        variable (string): Variable to extract.
    
    Returns:
        xarray: Icon grib file data.
    """
    grib_data = xarray.open_dataarray(file, engine='cfgrib',
                    backend_kwargs=dict(filter_by_keys={'shortName': variable}))

    geographics = _get_icon_metadata(grib_data)
    grib_data = grib_data.rio.write_crs(geographics['crs'])

    # Rename coordinates for further reprojection
    grib_data = grib_data.rename({'longitude':'x','latitude':'y'})

    return grib_data


def _get_icon_metadata(xarray_var):
    """Get projection of an Icon xarray.

    Args:
        xarray_var (xarray): Icon grib data.

    Returns:
        dict: Coordinate reference system.
    """
    projparams = proj4_from_grib(xarray_var)
    crs_model = pyproj.crs.CRS.from_dict(projparams)

    return {'crs': crs_model}


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
    grib_data = grib_data.drop_vars(['latitude', 'longitude'], errors='ignore')

    return grib_data


def _get_moloch_metadata(moloch_data: xarray.DataArray) -> dict:
    """Get projection and geographic extent of a Moloch xarray.

    Args:
        xarray_var (xarray): Moloch grib data.

    Returns:
        dict: Projection and geographic extent of Moloch xarray.
    """
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
    grib_data = grib_data.drop_vars(['latitude', 'longitude'], errors='ignore')

    return grib_data


def _get_bolam_metadata(bolam_data: xarray.DataArray) -> dict:
    """Get projection and geographic extent of a Bolam xarray.

    Args:
        xarray_var (xarray): Bolam grib data.

    Returns:
        dict: Projection and geographic extent of Bolam xarray.
    """
    bolam_projection = proj4_from_grib(bolam_data)

    x_0 = bolam_data.attrs['GRIB_longitudeOfFirstGridPointInDegrees'] - 360.0
    d_x = bolam_data.attrs['GRIB_iDirectionIncrementInDegrees']

    y_0 = bolam_data.attrs['GRIB_latitudeOfFirstGridPointInDegrees']
    d_y = bolam_data.attrs['GRIB_jDirectionIncrementInDegrees']

    return {'x0': x_0, 'dx': d_x, 'y0': y_0, 'dy': d_y,
            'crs': bolam_projection,
            'x_size': bolam_data.attrs['GRIB_Nx'],
            'y_size': bolam_data.attrs['GRIB_Ny']}


def read_arome_grib(grib_file: str, variable: str) -> xarray.DataArray:
    """Reads an AROME grib file and transforms it into an xarray.DataArray.

    Args:
        grib_file (str): Path to an AROME grib file.
        variable (str): Variable to extract.

    Returns:
        xarray: AROME grib file data.
    """
    grib_filter = {'shortName': variable}

    grib_data = xarray.open_dataarray(grib_file, engine='cfgrib',
                    backend_kwargs={'filter_by_keys': grib_filter})

    grib_md = _get_arome_metadata(grib_data)

    grib_data.rio.write_crs(grib_md['crs'], inplace=True)

    # Rename coordinates for further reprojection
    grib_data = grib_data.rename({'longitude':'x','latitude':'y'})

    return grib_data


def _get_arome_metadata(arome_data: xarray.DataArray) -> dict:
    """Get projection of an AROME xarray.

    Args:
        xarray_var (xarray): AROME grib data.

    Returns:
        dict: Coordinate reference system.
    """
    projparams=proj4_from_grib(arome_data)
    crs_model= pyproj.crs.CRS.from_dict(projparams)

    return {'crs': crs_model}


def read_arpege_grib(grib_file: str, variable: str) -> xarray.DataArray:
    """Reads an ARPEGE grib file and transforms it into an xarray.DataArray.

    Args:
        grib_file (str): Path to an ARPEGE grib file.
        variable (str): Variable to extract.

    Returns:
        xarray: ARPEGE grib file data.
    """
    grib_filter = {'shortName': variable}

    grib_data = xarray.open_dataarray(grib_file, engine='cfgrib',
                    backend_kwargs={'filter_by_keys': grib_filter})

    grib_md = _get_arpege_metadata(grib_data)


    grib_data.rio.write_crs(grib_md['crs'], inplace=True)

    # Rename coordinates for further reprojection
    grib_data = grib_data.rename({'longitude':'x','latitude':'y'})

    return grib_data


def _get_arpege_metadata(arpege_data: xarray.DataArray) -> dict:
    """Get projection of an ARPEGE xarray.

    Args:
        xarray_var (xarray): ARPEGE grib xarray.

    Returns:
        dict: Coordinate reference system.
    """
    projparams = proj4_from_grib(arpege_data)
    crs_model = pyproj.crs.CRS.from_dict(projparams)

    return {'crs': crs_model}

def read_ecmwf_hres_grib(file: str, variable: str, model: str):
    """Reads an ECMWF-HRES grib file and transforms it into an
    xarray.DataArray.

    Args:
        grib_file (str): Path to an AROME grib file.
        variable (str): Variable to extract.
        model (str): Model name.

    Returns:
        xarray: AROME grib file data.
    """
    grib_data = xarray.open_dataarray(file, engine='cfgrib',
                    backend_kwargs=dict(filter_by_keys={'shortName': variable}))

    if variable == 'tp':
        grib_data.data = grib_data.data * 1000
        grib_data.attrs['units'] = 'mm'
        grib_data.attrs['GRIB_units'] = 'mm'


    geographics = _get_ecmwf_hres_metadata(grib_data)
    grib_data = grib_data.rio.write_crs(geographics['crs'])

    # Rename coordinates for further reprojection
    grib_data = grib_data.rename({'longitude':'x','latitude':'y'})

    grib_data = grib_data.assign_coords(model=model)
    grib_data = grib_data.expand_dims(['model', 'time'])

    return grib_data


def _get_ecmwf_hres_metadata(xarray_var):
    """Gets projection of an ECMWF-HRES xarray.

    Args:
        xarray_var (xarray): ECMWF-HRES grib data.

    Returns:
        dict: Coordinate reference system.
    """
    projparams = proj4_from_grib(xarray_var)
    crs_model = pyproj.crs.CRS.from_dict(projparams)

    return {'crs': crs_model}
