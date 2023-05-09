Downscaling
===========

Exemple 1: reprojeccions i interpolacions
*****************************************

En aquest exemple suposarem que ja tenim carregat un `xarray.DataArray` a la variable `nwp_data`.

Comencem primer amb dues interpolacions (bilinear i nearest) que no impliquen una reprojecció,
sinó que es treballa en la projecció de l'`xarray.DataArray` d'entrada. Això s'aconsegueix no
informant de la projecció a les funcions :py:func:`unimodel.downscaling.interpolation.bilinear` i
:py:func:`unimodel.downscaling.interpolation.nearest`.

.. code-block:: python
    
    from unimodel.downscaling.interpolation import bilinear, nearest

    rep_data = bilinear(nwp_data, config['corner_ul'], config['grid_shape'],
                        config['grid_res'])

    rep_data = nearest(nwp_data, config['corner_ul'], config['grid_shape'],
                       config['grid_res'])

Repetim l'exemple anterior, però en aquest cas, informant una projecció. Així, a part de la
interpolació es farà una reprojecció mitjançant una de les dues metodologies que indiquem,
bilinear o nearest.

.. code-block:: python
    
    from unimodel.downscaling.interpolation import bilinear, nearest

    rep_data = bilinear(nwp_data, config['corner_ul'], config['grid_shape'],
                        config['grid_res'], 'epsg:4326')

    rep_data = nearest(nwp_data, config['corner_ul'], config['grid_shape'],
                       config['grid_res'], 'epsg:4326')

Les funcions :py:func:`unimodel.downscaling.interpolation.bilinear` i
:py:func:`unimodel.downscaling.interpolation.nearest` no deixen de ser un cas concret de 
l'aplicació de la funció :py:func:`unimodel.utils.geotools.reproject_xarray`.

Exemple 2: Correcció per elevació
*********************************

En aquest apartat es mostra el funcionament de la classe :py:class:`Ecorrection` 
del mòdul :py:module:`Downscaling` del paquet **unimodel**.

La idea de aquesta funció és aplicar una correcció per elevació al camp de la temperatura.
Per això, s'aplica un lapse rate de temperatura a les diferències d'altitud entre 
l'orografia nativa del NWP i la desitjada seguint la següent equació:

.. math::

    T_{1km} = T_{3km} - \\gamma\\cdot(z_{1km} - z_{3km})

on :math:`T` és la temperatura, :math:`\\gamma` és el lapse rate, :math:`z_{1km}` és l'altitut
donada per un model de terreny digital (dem) amb 1 km de longitud de quadrícula i :math:`z_{3km}`
l'altitud del model NWP natiu amb una resolució de 3 km.

El lapse rate per a cada pixel es calcula a partir dels píxels dels veïns més propers. Aquests 
pixels són només aquells que estàn a terra. Es calcula utilitzant el mètode dels mínims quadrats
tenint en compte la temperatura i l'altitut.

En aquest exemple importarem i llegirem la simulació de les 00 UTC del model WRF del 24 de febrer 
del 2022 per a l'horitzó de pronòstic 10. Es carregarà un `xarray.DataArray` per a cada variable: 
land_sea_mask, `nwp_lsm`, per inicialitzar la classe, i temperatura, `da_2t` i orografia, `da_orog`, 
com a paràmetres de la funció que aplica la correcció :py:function:`apply_correction`.

.. code-block:: python

    from datetime import datetime

    import unimodel.io
    from unimodel.io.importers_nwp import import_nwp_grib
    from unimodel.utils.load_config import load_config
    from unimodel.downscaling.ecorrection import Ecorrection

    if __name__ == '__main__':

        # Definim els paràmetres inicials
        date = datetime(2022, 2, 24, 0)
        model = 'wrf_ecm'
        lead_time = 10
        config = load_config('path-al-config')
        
        # Copiem el fitxer des del Filer fins al directori de treball
        nwp_file = import_nwp_grib(date, lead_time, model, config)
        
        # Importem el lector a través de la interfície, el 'reader' és 
        # equivalent a 'read_wrf_grib_prs'
        reader = unimodel.io.get_reader(model)
        
        # Cridem la funció reader on llegim la variable 'lsm'
        nwp_lsm = reader(nwp_file, 'lsm', model)

        dem_file = 'tests/data/test_data/hres_dem_25831.tif'
        
        ecorr = Ecorrection(nwp_lsm, dem_file)

        da_2t = reader(nwp_file, '2t', model)
        da_orog = reader(nwp_file, 'orog', model)

        da_2t_corrected = ecorr.apply_correction(da_2t, da_orog)

En cas de que volguéssim tenir en compte el land_sea_mask, a la funció :py:function:`apply_correction`,
posaríem `land_sea_mask=True`.
