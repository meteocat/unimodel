"""Subrutines for retrieve geographical features
"""
import numpy as np


def _get_key(attribs, key, default=None):
    """get key if it exists, otherwise return default value (default None)"""
    if key in attribs:
        return attribs[key]
    else:
        return default


def proj4_from_grib(ds_grib):
    """
    ES UNA COPIA DE UNA SUBRUTINA DEL PYGRIB
    sets the ``projparams`` instance variable to a dictionary containing
    proj4 key/value pairs describing the grid.
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
    elif attributes['gridType'] == 'space_view':
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
    elif attributes['gridType'] == "lambert_azimuthal_equal_area":
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
