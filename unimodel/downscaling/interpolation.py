"""Interpolation module.
"""
import xarray
from rasterio.warp import Resampling

from unimodel.utils.geotools import reproject_xarray


def bilinear(data: xarray.DataArray, corner_ul: tuple, grid_shape: tuple,
             grid_res: tuple, dest_proj: str = None) -> xarray.DataArray:
    """Interpolates an xarray to a desired resolution and bounds using the
    bilinear resampling method. If dest_projection is informed, a reprojection
    is also done.

    Args:
        data (xarray.Datarray): Data to interpolate.
        corner_ul (tuple): Upper left corner of the target grid.
        grid_shape (tuple): Shape of the target grid.
        grid_res (tuple): Spatial resolution of the target grid.
        dest_proj (str, optional): Projection of the targe grid (proj4 or OGC
                                   WKT). Defaults to None, no reprojection is
                                   assumed.

    Returns:
        xarray.Datarray: Interpolated data.
    """
    if dest_proj is None:
        dest_proj = data.rio.crs.to_proj4()

    grid_interp = reproject_xarray(data, dest_proj, grid_shape, corner_ul,
                                   grid_res, resampling=Resampling.bilinear)

    return grid_interp


def nearest(data: xarray.DataArray, corner_ul: tuple, grid_shape: tuple,
            grid_res: tuple, dest_proj: str = None) -> xarray.DataArray:
    """Interpolates an xarray to a desired resolution and bounds using the
    nearest resampling method. If dest_projection is informed, a reprojection
    is also done.

    Args:
        data (xarray.Datarray): Data to interpolate.
        corner_ul (tuple): Upper left corner of the target grid.
        grid_shape (tuple): Shape of the target grid.
        grid_res (tuple): Spatial resolution of the target grid.
        dest_proj (str, optional): Projection of the targe grid (proj4 or OGC
                                   WKT). Defaults to None, no reprojection is
                                   assumed.

    Returns:
        xarray.Datarray: Interpolated data.
    """
    if dest_proj is None:
        dest_proj = data.rio.crs.to_proj4()

    grid_interp = reproject_xarray(data, dest_proj, grid_shape, corner_ul,
                                   grid_res, resampling=Resampling.nearest)

    return grid_interp
