import pyproj
import xarray
from rasterio import Affine
from unimodel.utils.geotools import proj4_from_grib
import numpy as np


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

    # Calculem el CRS del WRF que contindrà bàsicament la projecció i paràmetres asssociats.
    crs_wrf = pyproj.CRS(
        '+proj=lcc +units=m +R=6370000'
        ' +lat_1=' + str(xarray_var.attrs['GRIB_Latin2InDegrees']) +
        ' +lat_2=' + str(xarray_var.attrs['GRIB_Latin1InDegrees']) +
        # ' +lat_0=' + str(xarray_var.attrs['GRIB_LaDInDegrees']) +
        ' +lat_0=40.70002' +
        ' +lon_0=' + str(xarray_var.attrs['GRIB_LoVInDegrees']) +
        ' +nadgrids=@null')
    
    # La informació que apareix en els fitxers grib qamb el que s'ha de construir l'afí (que 
    # relacionarà les coordenades de la matriu de dades amb les coordenades de la projecció del model)
    # estan en coordenades geogràfiques (lat,lon) i ens faria falta tenir-les en coordenades del model
    # (en el cas del WRF LAMBERT)

    crs_gcp = pyproj.CRS('EPSG:4326')

    # Tranformem les coordenades del afi en lat lon a coordenades de LAMBERT
    transformer = pyproj.Transformer.from_crs(crs_gcp, crs_wrf)

    # Up left corner of domain
    x0, y0 = transformer.transform(
        float(xarray_var.attrs['GRIB_latitudeOfFirstGridPointInDegrees']),
        float(xarray_var.attrs['GRIB_longitudeOfFirstGridPointInDegrees']))
    y0 = (ny-1) * dy + y0

    # En teoria l'AFI es deduiria a partir dels paràmetres anteriors però degut a errors
    # en el grib-prs del wrf es posa l'afí directament deduit a partir del gdalinfo
    wrfout_gt = (-252466.8378711785+1500, 3000.0, 0.0,
                 391438.10408251436-1500, 0.0, -3000.0)

    return {'affine': Affine.from_gdal(wrfout_gt[0], wrfout_gt[1],
                                       wrfout_gt[2], wrfout_gt[3],
                                       wrfout_gt[4], wrfout_gt[5]),
            # 'affine': Affine.from_gdal(x0, dx, 0, y0, 0, -dy),
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

    # La informació que apareix en els fitxers grib qamb el que s'ha de construir l'afí (que 
    # relacionarà les coordenades de la matriu de dades amb les coordenades de la projecció del model)
    # estan en coordenades geogràfiques (lat,lon) i ens faria falta tenir-les en coordenades del model
    # (latlon). Com que el model ja està en latlon en aquest cas el calcul del afí és fàcil.

    # Up left corner of domain
    x0 = xarray_var.attrs['GRIB_latitudeOfFirstGridPointInDegrees']
    y0 = xarray_var.attrs['GRIB_longitudeOfFirstGridPointInDegrees']

    # Increments
    dx = xarray_var.attrs['GRIB_iDirectionIncrementInDegrees']
    dy = xarray_var.attrs['GRIB_jDirectionIncrementInDegrees']



    return {'affine': Affine.from_gdal(x0, dx, 0, y0, 0, -dy),
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
    # import pickle
    # with open('xarray_geotools.pkl', 'wb') as file:
    #    pickle.dump(ds_data, file)
    geographics = _get_wrf_prs_metadata(ds_data)
    ds_data = ds_data.rio.write_crs(geographics['crs'])
    ds_data.rio.write_transform(geographics['affine'], inplace=True)
    
    # El grib del WRF produeixen un xarray sense coordenades i per evitar feina
    # innecessària al futur es decideix crear-les i anomenar-les x i y perquè
    # seran les que després s'usaran per reprojectar.

    x_coords = np.linspace(geographics['affine'].c,
                            geographics['affine'].c + (geographics['x_size'] *
                            geographics['affine'].a) - geographics['affine'].a,
                            geographics['x_size'])

    y_coords = np.linspace(geographics['affine'].f,
                            geographics['affine'].f + (geographics['y_size'] *
                            geographics['affine'].e) - geographics['affine'].e,
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
    ds_data.rio.write_transform(geographics['affine'], inplace=True)

    # Canviem els noms perquè amb coordenades x i y serà més fàcil reprojectar.
    ds_data = ds_data.rename({'longitude':'x','latitude':'y'})

    return ds_data