
from unimodel.utils.geotools import reproject_xarray
from rasterio.warp import Resampling
import xarray


def bilinear(data, corner_ul, grid_shape, grid_res, dest_proj=None):
    """Module for interpolating a xarray to a desired resolution using
    the bilinear methodology with possibility of reprojecting.

    Args:
        data (xarray.Datarray): data to be interpolated.
        corner_ul (tuple): Upper left corner of the target grid.
        grid_shape (tuple): dimensions of the target grid.
        grid_res (tuple): resolution of the target grid.
        dest_proj (str, optional): string indicating the projection.
        to be used, must be: proj4 o OGC WKT. Defaults to None.

    Returns:
        xarray.Datarray: xarray obtained after the interpolation
    """
    if dest_proj is None:
        dest_proj = data.rio.crs.to_proj4()
    grid_interp=reproject_xarray(data, dest_proj, grid_shape, corner_ul,
                               grid_res, resampling= Resampling.bilinear)
    return grid_interp


def nearest(data, corner_ul, grid_shape, grid_res, dest_proj=None):
    """Module for interpolating a xarray to a desired resolution using
    nearest methodology with possibility of reprojecting.

    Args:
        data (xarray.Datarray): data to be interpolated.
        corner_ul (tuple): Upper left corner of the target grid.
        grid_shape (tuple): dimensions of the target grid.
        grid_res (tuple): resolution of the target grid.
        dest_proj (str, optional): string indicating the projection.
        to be used, must be: proj4 o OGC WKT. Defaults to None.

    Returns:
        xarray.Datarray: xarray obtained after the interpolation
    """
    if dest_proj is None:
        dest_proj = data.rio.crs.to_proj4()
    grid_interp=reproject_xarray(data, dest_proj, grid_shape, corner_ul,
                               grid_res, resampling= Resampling.nearest)
    return grid_interp