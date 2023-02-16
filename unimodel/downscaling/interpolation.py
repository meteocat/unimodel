
from unimodel.utils.geotools import reproject_xarray
from rasterio.warp import Resampling


def bilinear(data, corner_ul, grid_shape, grid_res, dest_proj=None):
    if dest_proj is None:
        dest_proj = data.rio.crs.to_proj4()
    grid_interp=reproject_xarray(data, dest_proj, grid_shape, corner_ul,
                               grid_res, resampling= Resampling.cubic_spline)
    return grid_interp


def nearest(data, corner_ul, grid_shape, grid_res, dest_proj=None):
    if dest_proj is None:
        dest_proj = data.rio.crs.to_proj4()
    grid_interp=reproject_xarray(data, dest_proj, grid_shape, corner_ul,
                               grid_res, resampling= Resampling.nearest)
    return grid_interp