import pyproj
import xarray
from rasterio import Affine


def _get_wrf_prs_metadata(xarray_var):

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


def read_wrf_prs(file,variable):
    """Read wrf variable chosen in a wrf-PRS grib file

    Args:
        file (string): Path of the file which has to be readed
        variable (string): Variable to extract
    Returns:
        xarray: Contains the data and the geographical information to  
                transform the grids
    """

    ds_data = xarray.open_dataarray(file, engine='cfgrib',
                    backend_kwargs=dict(filter_by_keys={'shortName': variable}))
 
    geographics = _get_wrf_prs_metadata(ds_data)
    ds_data = ds_data.rio.write_crs(geographics['crs'])
    ds_data.rio.write_transform(geographics['affine'], inplace=True)

    return ds_data
