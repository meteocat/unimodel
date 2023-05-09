API
===

Input/Output
------------

Aquest mòdul és l'encarregat de la gestió de la importació dels fitxers grib
del Filer a un directori de treball.

.. automodule:: unimodel.io.importers_nwp
    :members:

Aquest mòdul inclou funcions per agrupar diversos `xarray.DataArray`, ja sigui de
diferents horitzons de pronòstic o de diferents models.

.. automodule:: unimodel.io.exporters
    :members:

.. _api-lectura:

Lectura
-------

Aquest mòdul inclou totes les funcions necessàries per poder llegir els fitxers
grib i transformar-los a `xarray.DataArray` amb les coordenades i projecció natives.

.. automodule:: unimodel.io.readers_nwp
    :members:


Downscaling
-----------

Aquest mòdul incorpora tres metodolgies per obtenir un camp a una resolució
més elevada: interpolació bilinear i del veí més proper i la correcció 
per elevació.

.. automodule:: unimodel.downscaling.interpolation
    :members:

.. automodule:: unimodel.downscaling.ecorrection
    :members:

Útils
-----

Aquest mòdul inclou funcions relacionades amb la reprojecció i l'extracció de la projecció
completa d'un fitxer grib.

.. automodule:: unimodel.utils.geotools
    :members:

Aquest mòdul facilita la importació del fitxer de configuració necessari per fer servir
l'unimodel.

.. automodule:: unimodel.utils.load_config
    :members:


.. _api-interficie:

Interfície
----------

Aquest mòdul facilita la importació de les funcions de lectura dels models. D'aquesta manera,
si es vol treballar amb més d'un model només cal importar una sola funció i no una per cada
model.

.. automodule:: unimodel.io.interface
    :members:
