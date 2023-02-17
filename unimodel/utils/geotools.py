"""Subrutines for retrieve geographical features
"""
import numpy as np
import rioxarray
import xarray
from rasterio import Affine
from rasterio.warp import Resampling


def reproject_xarray(xr_coarse: xarray.DataArray, dst_proj: str, shape: tuple,
                     ul_corner: tuple, resolution: tuple,  
                     resampling: Resampling = Resampling.cubic_spline) \
                     -> xarray.DataArray:
    """Reprojects an xarray based on crs, transform and shape of another xarray.

    Args:
        xr_coarse (xarray): xarray to reproject.
        xr_hres (xarray): xarray with characteristics to reproject to.
        resampling (Resampling, optional): Resampling method used for
            interpolation processes. Defaults to Resampling.cubic_spline.

    Returns:
        xarray: Reprojected xarray.
    """

    transform=Affine.from_gdal(ul_corner[0], resolution[0], 0,
                               ul_corner[1], 0, resolution[1])
    xr_reproj = xr_coarse.rio.reproject(dst_proj, shape=(shape[0], shape[1]),
                                        resampling=resampling,
                                        transform=transform)

    return xr_reproj


def _get_key(attribs: dict, key: str, default=None):
    """Get key if exists, otherwise return default value.

    Args:
        attribs (dict): Dictionary.
        key (str): Dictionary key.
        default (any, optional): Default value if key not exists. Defaults
                                 to None.

    Returns:
        any: Key value.
    """
    if key in attribs:
        return attribs[key]

    return default


def proj4_from_grib(ds_grib: xarray.DataArray) -> dict:
    """Gets proj4 string parameters as a dict from an xarray containing data
    from a NWP grib.

    Copyright 2010 Jeffrey Whitaker

    It is a copy of _set_proj_params from https://github.com/jswhit/pygrib
    /blob/40558bfeb7fc5c2a042496c1ed10c500e706efeb/src/pygrib/_pygrib.pyx.

    Args:
        ds_grib (xarray.DataArray): NWP grib data array.

    Raises:
        ValueError: If shape of the earth is unknown.
        KeyError: If projection center not found.

    Returns:
        dict: Projection params
    """
    projparams = {}

    attributes=ds_grib.attrs
    tolerate_badgrib = False
    missingvalue_int = attributes['GRIB_missingValue']

    # check for radius key, if it exists just use it
    # and don't bother with shapeOfTheEarth
    if 'GRIB_radius' in attributes:
        projparams['a'] = attributes['GRIB_radius']
        projparams['b'] = attributes['GRIB_radius']
    elif 'GRIB_shapeOfTheEarth' in attributes:
        if attributes['GRIB_shapeOfTheEarth'] == 6:
            projparams['a']=6371229.0
            projparams['b']=6371229.0
        elif attributes['GRIB_shapeOfTheEarth'] in [3,7]:
            if 'GRIB_scaleFactorOfMajorAxisOfOblateSpheroidEarth' in attributes:
                scalea = attributes['GRIB_scaleFactorOfMajorAxisOfOblateSpheroidEarth']
                scaleb = attributes['GRIB_scaleFactorOfMinorAxisOfOblateSpheroidEarth']
                if scalea and scalea is not missingvalue_int:
                    scalea = np.power(10.0,-scalea)
                    if attributes['GRIB_shapeOfTheEarth'] == 3: # radius in km
                        scalea = 1000.*scalea
                else:
                    scalea = 1
                if scaleb and scaleb is not missingvalue_int:
                    scaleb = np.power(10.0,-scaleb)
                    if attributes['GRIB_shapeOfTheEarth'] == 3: # radius in km
                        scaleb = 1000.*scaleb
                else:
                    scaleb = 1.
            else:
                scalea = 1.
                scaleb = 1.
                projparams['a']=attributes['GRIB_scaledValueOfEarthMajorAxis']*scalea
                projparams['b']=attributes['GRIB_scaledValueOfEarthMinorAxis']*scaleb
        elif attributes['GRIB_shapeOfTheEarth'] == 4:
            projparams['a']=6378137.0
            projparams['b']=6356752.314
        elif attributes['GRIB_shapeOfTheEarth'] == 2:
            projparams['a']=6378160.0
            projparams['b']=6356775.0
        elif attributes['GRIB_shapeOfTheEarth'] == 1:
            if 'GRIB_scaleFactorOfRadiusOfSphericalEarth' in attributes:
                scalea = attributes['GRIB_scaleFactorOfRadiusOfSphericalEarth']
                if scalea and scalea is not missingvalue_int:
                    scalea = np.power(10.0,-scalea)
                else:
                    scalea = 1
                scaleb = scalea
            else:
                scalea = 1.
                scaleb = 1.
            projparams['a']=attributes['GRIB_scaledValueOfRadiusOfSphericalEarth']*scalea
            projparams['b']=attributes['GRIB_scaledValueOfRadiusOfSphericalEarth']*scaleb
        elif attributes['GRIB_shapeOfTheEarth'] == 0:
            projparams['a']=6367470.0
            projparams['b']=6367470.0
        elif attributes['GRIB_shapeOfTheEarth'] == 5: # WGS84
            projparams['a']=6378137.0
            projparams['b']=6356752.3142
        elif attributes['GRIB_shapeOfTheEarth'] == 8:
            projparams['a']=6371200.0
            projparams['b']=6371200.0
        else:
            if not tolerate_badgrib:
                raise ValueError('unknown shape of the earth flag')

    if attributes['GRIB_gridType'] in ['reduced_gg','reduced_ll','regular_gg','regular_ll']:
        # regular lat/lon grid
        projparams['proj']='longlat'
    elif attributes['GRIB_gridType'] == 'polar_stereographic':
        projparams['proj']='stere'
        projparams['lat_ts']=attributes['GRIB_latitudeWhereDxAndDyAreSpecifiedInDegrees']
        if 'GRIB_projectionCentreFlag' in attributes:
            projcenterflag = attributes['GRIB_projectionCentreFlag']
        elif 'GRIB_projectionCenterFlag' in attributes:
            projcenterflag = attributes['GRIB_projectionCenterFlag']
        else:
            if not tolerate_badgrib:
                raise KeyError('cannot find projection center flag')
        if projcenterflag == 0:
            projparams['lat_0'] = 90.
        else:
            projparams['lat_0'] = -90.
        projparams['lon_0']=attributes['GRIB_orientationOfTheGridInDegrees']
    elif attributes['GRIB_gridType'] == 'lambert':
        projparams['proj']='lcc'
        projparams['lon_0']=attributes['GRIB_LoVInDegrees']
        projparams['lat_0']=attributes['GRIB_LaDInDegrees']
        projparams['lat_1']=attributes['GRIB_Latin1InDegrees']
        projparams['lat_2']=attributes['GRIB_Latin2InDegrees']
    elif attributes['GRIB_gridType'] =='albers':
        projparams['proj']='aea'
        scale = float(attributes['GRIB_grib2divider'])
        projparams['lon_0']=attributes['GRIB_LoV']/scale
        if attributes['GRIB_truncateDegrees']:
            projparams['lon_0'] = int(projparams['lon_0'])
        projparams['lat_0']=attributes['GRIB_LaD']/scale
        if attributes['GRIB_truncateDegrees']:
            projparams['lat_0'] = int(projparams['lat_0'])
        projparams['lat_1']=attributes['GRIB_Latin1']/scale
        if attributes['GRIB_truncateDegrees']:
            projparams['lat_1'] = int(projparams['lat_1'])
        projparams['lat_2']=attributes['GRIB_Latin2']/scale
        if attributes['GRIB_truncateDegrees']:
            projparams['lat_2'] = int(projparams['lat_2'])
    elif attributes['GRIB_gridType'] == 'space_view':
        projparams['lon_0']=attributes['GRIB_longitudeOfSubSatellitePointInDegrees']
        projparams['lat_0']=attributes['GRIB_latitudeOfSubSatellitePointInDegrees']
        if projparams['lat_0'] == 0.: # if lat_0 is equator, it's a
            projparams['proj'] = 'geos'
        # general case of 'near-side perspective projection' (untested)
        else:
            projparams['proj'] = 'nsper'
        scale = float(attributes['GRIB_grib2divider'])
        projparams['h'] = projparams['a'] * attributes['GRIB_Nr']/scale
        # h is measured from surface of earth at equator.
        projparams['h'] = projparams['h']-projparams['a']
    elif attributes['GRIB_gridType'] == "equatorial_azimuthal_equidistant":
        projparams['lat_0'] = attributes['GRIB_standardParallel']/1.e6
        projparams['lon_0'] = attributes['GRIB_centralLongitude']/1.e6
        projparams['proj'] = 'aeqd'
    elif attributes['GRIB_gridType'] == "lambert_azimuthal_equal_area":
        projparams['lat_0'] = attributes['GRIB_standardParallel']/1.e6
        projparams['lon_0'] = attributes['GRIB_centralLongitude']/1.e6
        projparams['proj'] = 'laea'
    elif attributes['GRIB_gridType'] == 'mercator':
        scale = _get_key(attributes, 'GRIB_grib2divider',False)
        if scale:
            scale = float(scale)
        else:
            scale = 1000.
        lon1 = attributes['GRIB_longitudeOfFirstGridPoint']/scale
        lon2 = attributes['GRIB_longitudeOfLastGridPoint']/scale
        if _get_key(attributes, 'GRIB_truncateDegrees',False):
            lon1 = int(lon1)
            lon2 = int(lon2)
        if _get_key(attributes, 'GRIB_LaD', False):
            projparams['lat_ts'] = attributes['GRIB_LaD']/scale
        else:
            projparams['lat_ts'] = attributes['GRIB_Latin']/scale
        if lon2 < lon1:
            lon2 += 360. # domain crosses Greenwich
        projparams['lon_0']=0.5*(lon1+lon2)
        projparams['proj']='merc'
    elif attributes['GRIB_gridType'] in ['rotated_ll','rotated_gg']:
        rot_angle = attributes['GRIB_angleOfRotationInDegrees']
        pole_lat = attributes['GRIB_latitudeOfSouthernPoleInDegrees']
        pole_lon = attributes['GRIB_longitudeOfSouthernPoleInDegrees']
        projparams['o_proj']='longlat'
        projparams['proj']='ob_tran'
        projparams['o_lat_p']=-pole_lat
        projparams['o_lon_p']=rot_angle
        projparams['lon_0']=pole_lon
    else: # unsupported grid type.
        projparams = None

    return projparams
