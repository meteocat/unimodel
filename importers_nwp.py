import numpy as np
import pyproj
import xarray
from rasterio import Affine

from unimodel.utils.geotools import proj4_from_grib


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

    # Degut a que el WRF-PRS es genera malament (el lat_0 no està definit) es posa la projecció 
    # del WRF harcoded tal com està definida en la versió actual del WRF de 3 km.
    crs_wrf = pyproj.CRS(
        '+proj=lcc +units=m +R=6370000'
        ' +lat_1= 60.0' +
        ' +lat_2= 30.0' + 
        ' +lat_0= 40.70002' +
        ' +lon_0= -1.5' +
        ' +nadgrids=@null')
    
    # Pel fet que el WRF-PRS està en format GRIB1 i té menys decimals es creen errors de metres
    # que es propaguen. Per aquest sentit es proposa usar els valors calculats directament a partir
    # de les metodolodies explicades a: 
    # https://meteocat.atlassian.net/wiki/spaces/RAM/pages/2820702244/Geotransform+WRF
    # El geotransform calculat allà perl WRF de 3 km és:
    # wrfout_gt = (-252466.8378711785, 3000.0, 0.0, 391438.10408251436, 0.0, -3000.0)
    # Així doncs: 


    # Upper left pixel centre donat per algoritme anterior
    x0 = -252466.8378711785
    y0 = 391438.10408251436

    # Perquè el xarray treballa amb el centre del pixel i el gdal ens mostra el corner superior esquerre
    # fem canvis:
    x0 = x0 + dx/2
    y0 = y0 - dy/2

    # Passem -dy perquè es decreixent.

    return { 'x0': x0, 'y0':y0, 'dx':dx, 'dy':-dy,
            'crs': crs_wrf, 'x_size': nx, 'y_size': ny}


def _get_icon_metadata(xarray_var):
    """Get projection, Affine transform and shape from an xarray.

    Args:
        xarray_var (xarray): xarray to get information from.

    Returns:
        dict: CRS, x size, y size and Affine transform.
    """

    nx = xarray_var.attrs['GRIB_Nx']
    ny = xarray_var.attrs['GRIB_Ny']

    # Llegim la projeccion associatda al xarray i la escrivim com CRS.
    projparams=proj4_from_grib(xarray_var)
    crs_model= pyproj.crs.CRS.from_dict(projparams)

    # La informació que apareix en els fitxers grib estan en coordenades geogràfiques (lat,lon) 
    # equiespaiades la qual cosa fa senzill definir l'afí

    # Low left corner of domain
    x0 = xarray_var.attrs['GRIB_longitudeOfFirstGridPointInDegrees']
    y0 = xarray_var.attrs['GRIB_latitudeOfFirstGridPointInDegrees']

    # Increments
    dx = xarray_var.attrs['GRIB_iDirectionIncrementInDegrees']
    dy = xarray_var.attrs['GRIB_jDirectionIncrementInDegrees']

    # Upper left corner of domain


    return {'affine': Affine.from_gdal(x0, dx, 0, y0+dy*ny, 0, -dy),
            'crs': crs_model, 'x_size': nx, 'y_size': ny}




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
    
    # El grib del WRF produeixen un xarray sense coordenades i per evitar feina
    # innecessària al futur es decideix crear-les i anomenar-les x i y perquè
    # seran les que després s'usaran per reprojectar.

    x_coords = np.linspace(geographics['x0'],
                           geographics['x0'] + ((geographics['x_size'] -1) *
                            geographics['dx']),
                            geographics['x_size'])

    y_coords = np.linspace(geographics['y0'],
                            geographics['y0'] + ((geographics['y_size'] -1)*
                            geographics['dy']),
                            geographics['y_size'])
    y_coords = y_coords[::-1]

    ds_data = ds_data.assign_coords(x=x_coords, y=y_coords)
    ds_data = ds_data.drop_vars(['latitude', 'longitude'], errors='ignore')


    return ds_data


def read_icon(file,variable):
    """Read wrf variable chosen in a ICON grib file

    Args:
        file (string): Path of the file which has to be readed
        variable (string): Variable to extract
    Returns:
        xarray: Contains the data and the geographical information to  
                transform the grids
    """
    ds_data = xarray.open_dataarray(file, engine='cfgrib',
                    backend_kwargs=dict(filter_by_keys={'shortName': variable}))

    geographics = _get_icon_metadata(ds_data)
    ds_data = ds_data.rio.write_crs(geographics['crs'])

    # Canviem els noms perquè amb coordenades x i y serà més fàcil reprojectar.
    ds_data = ds_data.rename({'longitude':'x','latitude':'y'})

    return ds_data