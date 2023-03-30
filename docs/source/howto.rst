Com funciona?
=============

En aquest apartat mostrem de forma breu i amb exemples el funcionament del paquet
**unimodel**.

Models disponibles
------------------

El paquet no disposa d'una funció genèrica que permeti treballar amb tots els models, sinó
que són específiques per a cada model disponible. Les funcions per transformar un fitxer grib
a `xarray.DataArray` es troben a :ref:`api-lectura`. La columna interfície correspon al nom
que cal indicar per importar la funció a través de la funció ``get_reader`` de
:ref:`api-interficie`.

+-----------------+----------------+------------------------------------------------------------+
| Model           | Interfície     | Funció                                                     | 
+=================+================+============================================================+
| Arome           | 'arome'        | :py:func:`unimodel.io.readers_nwp.read_arome_grib`         | 
+-----------------+----------------+------------------------------------------------------------+
| Arpege          | 'arpege'       | :py:func:`unimodel.io.readers_nwp.read_arpege_grib`        | 
+-----------------+----------------+------------------------------------------------------------+
| Bolam           | 'bolam'        | :py:func:`unimodel.io.readers_nwp.read_bolam_grib`         | 
+-----------------+----------------+------------------------------------------------------------+
| ECMWF-HRES      | 'ecmwf_hres'   | :py:func:`unimodel.io.readers_nwp.read_ecmwf_hres_grib`    | 
+-----------------+----------------+------------------------------------------------------------+
| ICON            | 'icon'         | :py:func:`unimodel.io.readers_nwp.read_icon_grib`          | 
+-----------------+----------------+------------------------------------------------------------+
| Moloch-GFS      | 'moloch_gfs'   | :py:func:`unimodel.io.readers_nwp.read_moloch_grib`        | 
+-----------------+----------------+------------------------------------------------------------+
| Moloch-ECMWF    | 'moloch_ecmwf' | :py:func:`unimodel.io.readers_nwp.read_moloch_grib`        | 
+-----------------+----------------+------------------------------------------------------------+
| Unified Model   | 'unified_model'| :py:func:`unimodel.io.readers_nwp.read_unified_model_grib` | 
+-----------------+----------------+------------------------------------------------------------+
| WRF-ECM         | 'wrf_ecm'      | :py:func:`unimodel.io.readers_nwp.read_wrf_prs`            | 
+-----------------+----------------+------------------------------------------------------------+
| WRF-EXP         | 'wrf_exp'      | :py:func:`unimodel.io.readers_nwp.read_wrf_prs`            | 
+-----------------+----------------+------------------------------------------------------------+
| WRF-GFS-3km     | 'wrf_gfs_3'    | :py:func:`unimodel.io.readers_nwp.read_wrf_prs`            | 
+-----------------+----------------+------------------------------------------------------------+
| WRF-GFS-9km     | 'wrf_gfs_9'    | :py:func:`unimodel.io.readers_nwp.read_wrf_prs`            | 
+-----------------+----------------+------------------------------------------------------------+
| WRF-TL-ENS      | 'wrf_tl_ens'   | :py:func:`unimodel.io.readers_nwp.read_wrf_tl_ens_grib`    | 
+-----------------+----------------+------------------------------------------------------------+


Fitxer de configuració
----------------------

Cal tenir un fitxer de configuració per poder córrer la majoria de funcions del paquet.
A continuació indiquem què ha de tenir, com a mínim, aquest fitxer .json.

.. code-block:: json

    {
        "nwp_dir": "Ruta al directori de treball on es copiaran els fitxers grib des del Filer",
        
        "lead_times": "int amb el nombre d'horitzons de pronòstic a considerar",

        "corner_ul": "cantonada superior esquerra [coordenada-x, coordenada-y]",
        "grid_shape": "mida de la matriu final [nombre-de-files, nombre-de-columnes]",
        "grid_res": "resolució espacial de la matriu final [resolució-en-x, resolució-en-y]",


        "{nom-model-1}" : {
                            "src_tar": "Ruta a un fitxer .tar.gz",
                            "src": "Nom del fitxer grib dins del .tar.gz",
                            "compressed": "True, indica que s'ha d'importar i descomprimir"
                          },
        
        "{nom-model-2}" : {
                            "src": "Nom del fitxer grib dins del .tar.gz",
                            "compressed": "False, indicant que només s'ha d'importar"
                          }
    }

Exemples
--------

En aquest apartat mostrem alguns exemples amb l'execució de diverses funcions que inclou el
paquet **unimodel**.

Definim primer el fitxer de configuració, en el qual inclourem dos models, l'Arome i l'Arpege.

.. code-block:: json

    {
        "nwp_dir": "/data/RECERCA/software_data/pme/nwp_stage/",
        
        "lead_times": 73,

        "corner_ul": [-1.6211310000000103, 43.4553730000000016],
        "grid_shape": [620, 417],
        "grid_res": [0.010642, 0.010642],

        "arpege": {
                    "src_tar": "/data/dades/ARPEGE/arpege-11.{year}{month}{day}{run}.tar.gz",
                    "src": "arpege-11.{year}{month}{day}{run}_{lt}.grib2",
                    "compressed": true
                  },
        "arome":  {
                    "src_tar": "/data/dades/AROME/arome-1p1.{year}{month}{day}{run}.tar.gz",
                    "src": "arome-1p1.{year}{month}{day}{run}_{lt}.grib2",
                    "compressed": true
                  }
    }


Exemple 1: lectura d'un sol model
*********************************

En aquest exemple importarem i llegirem només la simulació de les 00 UTC del model
Arome del 24 de febrer del 2022 per a l'horitzó de pronòstic 10.

.. code-block:: python

    from datetime import datetime

    import unimodel.io
    from unimodel.downscaling.interpolation import bilinear
    from unimodel.io.importers_nwp import import_nwp_grib
    from unimodel.utils.load_config import load_config

    # Definim els paràmetres inicials
    date = datetime(2022, 2, 24, 0)
    model = 'arome'
    lead_time = 10
    config = load_config('path-al-config')
    
    # Copiem el fitxer des del Filer fins al directori de treball
    nwp_file = import_nwp_grib(date, lead_time, model, config)
    
    # Importem el lector a través de la interfície, el 'reader' és 
    # equivalent a 'read_arome_grib'
    reader = unimodel.io.get_reader(model)
    
    # Cridem la funció reader on llegim la variable 'tp'
    nwp_data = reader(nwp_file, 'tp', model)

.. _exemple-2:

Exemple 2: lectura de més d'un model
************************************

En aquest exemple importarem i llegirem la simulació de les 00 UTC dels models
Arome i Arpege del 24 de febrer del 2022 per a l'horitzó de pronòstic 10. A més,
els unirem en un sol xarray.DataArray i ho exportarem a netcdf.

.. code-block:: python

    from datetime import datetime

    import unimodel.io
    from unimodel.downscaling.interpolation import bilinear
    from unimodel.io.importers_nwp import import_nwp_grib
    from unimodel.io.exporters import merge_models
    from unimodel.utils.load_config import load_config

    # Definim els paràmetres inicials
    date = datetime(2022, 2, 24, 0)
    models = ['arome', 'arpege']
    lead_time = 10
    config = load_config('path-al-config')
    
    models_data = []
    for model in models:
        # Copiem el fitxer des del Filer fins al directori de treball
        nwp_file = import_nwp_grib(date, lead_time, model, config)
        
        # Importem el lector a través de la interfície, el 'reader' és 
        # equivalent a 'read_arome_grib'
        reader = unimodel.io.get_reader(model)
        
        # Cridem la funció reader on llegim la variable 'tp'
        nwp_data = reader(nwp_file, 'tp', model)

        # Afegim la sortida de cadascun dels models a una sola llista
        models_data.append(nwp_data)
    
    # Una vegada tenim els models en una llista, els podem unir en un
    # sol xarray.DataArray mitjançant la funció merge models
    model_data = merge_models(models_data)

    # I si ho volguéssim exportar a netcdf només ens cal fer el següent:
    model_data.to_netcdf('fitxer-de-sortida', engine='netcdf4')


Exemple 3: reprojeccions i interpolacions
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

Exemple 4: script obtenció PME
******************************

El darrer exemple és una prova per obtenir tots els models del Poor Man's Ensemble en
un sol `xarray.DataArray`. L'exemple és similar a :ref:`exemple-2`, però amb més models i tots
els horitzons de pronòstic. S'utilitza també la llibreria `dask <https://www.dask.org/>`_.

.. code-block:: python

    """Main script to create an ensemble from different NWP model gribs.
    """
    from datetime import datetime

    import dask

    import unimodel.io
    from unimodel.downscaling.interpolation import bilinear
    from unimodel.io.exporters import concat_and_merge
    from unimodel.io.importers_nwp import import_nwp_grib
    from unimodel.utils.load_config import load_config


    def __process_model(model, date, config):
        """Processes and interpolates each model to a common grid.

        Args:
            model (str): NWP model name.
            date (datetime): Run date of NWP model.
            config (dict): Configuration dictionary

        Returns:
            list: xarray including all lead times of NWP model run.
        """
        out_model = []
        for lead_time in range(config['lead_times']):
            nwp_file = import_nwp_grib(date, lead_time, model, config)
            reader = unimodel.io.get_reader(model)
            nwp_data = reader(nwp_file, 'tp', model)
            rep_data = bilinear(nwp_data, config['corner_ul'],
                                config['grid_shape'], config['grid_res'],
                                'epsg:4326')
            out_model.append(rep_data)

        return out_model


    def main():
        """Creates an ensemble from different NWP model grib files.
        """
        # Definim variables a partir del fitxer de configuració
        config = load_config('config_unimodel.json')

        models = ['wrf_gfs_9', 'wrf_gfs_3', 'wrf_exp', 'wrf_ecm',
                'moloch_ecm', 'moloch_gfs', 'ecmwf_hres', 'arome',
                'bolam', 'icon', 'arpege']

        date = datetime(2023, 2, 24)

        time_total_0 = datetime.utcnow()
        lazy_results = []
        for model in models:
            lazy_result = dask.delayed(__process_model)(model, date, config)
            lazy_results.append(lazy_result)

        processed = dask.compute(*lazy_results)

        xarray_data = concat_and_merge(processed)

        # Convert xarray to netcdf
        xarray_data.to_netcdf(config['netcdf_output'], engine='netcdf4')

        time_total_1 = datetime.utcnow()
        print((time_total_1 - time_total_0).total_seconds() / 60)


    if __name__ == '__main__':

        main()
