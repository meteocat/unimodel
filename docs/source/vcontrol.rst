Control de versions
===================


v0.2.3 - 12/07/2023
-------------------

- S'afegeix la lectura del grib de l'ensemble de l'ECMWF mitjançant la funció :py:func:`unimodel.io.readers_nwp.read_ecmwf_ens_grib`.
- Correcció de petits bugs dels tests.

v0.2.2 - 06/07/2023
-------------------

- La lectura del model WRF-GFS-9km era errònia degut a la diferència d'extensió amb la resta de models WRF pels quals estava implementada la funció :py:func:`unimodel.io.readers_nwp.read_wrf_tl_ens_grib`.
- Es corregeix afegint un paràmetre a la funció :py:func:`unimodel.io.readers_nwp._get_wrf_prs_metadata` que controla si el model és ``wrf_gfs_9`` per aplicar una extensió diferent a la resta de models WRF considerats.


v0.2.1 - 20/06/2023
-------------------

.. _Numba: https://numba.pydata.org/

- S'implementa una millora en l'eficiència del càlcul del gradient a la metodologia que obté un refinament del camp de temperatura :py:func:`unimodel.downscaling.ecorrection.Ecorrection`. L'optimització s'obté mitjançant la llibreria Numba_.
- Es reorganitza la importació de la màscara terra-mar a partir d'un shapefile per augmentar l'eficiència de la funció :py:func:`unimodel.downscaling.ecorrection.Ecorrection.apply_correction`.


v0.2.0 - 19/05/2023
-------------------

- Incorporació d'una metodologia per a obtenir un refinament del camp de temperatura :py:func:`unimodel.downscaling.ecorrection.Ecorrection`. Un exemple d'implementació d'aquesta nova funció es pot torbar a :ref:`downscaling-ecorr`.
- Correcció bug a l'hora de fer la reprojecció, el shape es passava com (columnes, files) i ara s'ha corregit a (files, columnes). Afecta a la reprojecció de sortida.

v0.1.2 - 11/04/2023
-------------------

- S'adapta la importació dels gribs tenint en compte que hi pot haver fitxer descomprimits que tinguin el mateix nom, ja que poden no contenir informació de la data i només de l'horitzó de pronòstic (``{lt}``). Així és el cas d'alguns gribs del model WRF.

v0.1.1 - 31/03/2023
-------------------

Correció de diversos bugs:

- Es controla quan el fitxer que es vol importar no es troba dins del fitxer comprimit. Es fa un raise de ``FileNotFoundError``.
- El paràmetre ``{lt}`` dels fitxers de model ``src`` al fitxer de configuració pot variar el nombre de digits en funció del model. S'afegeix el paràmetre ``lead_time_digits`` al fitxer de configuració per controlar-ho.
- Es millora el ``match`` de les expressions regulars per a importar fitxers de model.


v0.1.0 - 28/03/2023
-------------------

Aquesta nova versió incorpora els següents canvis:

- Lectura dels fitxers de l'Unified Model (UM) mitjançant la funció :py:func:`unimodel.io.readers_nwp.read_unified_model_grib`.
- Lectura dels fitxers del time-lagged ensemble del WRF (WRF-TL-ENS) mitjançant la funció :py:func:`unimodel.io.readers_nwp.read_wrf_tl_ens_grib`. 
- Funció que permet allargar l'hortizó de pronòstic d'un model amb un valor constant de ``np.nan``. 

v0.0.0 - 06/03/2023
-------------------

Primera versió operativa del paquet de Python **unimodel**. Aquesta inclou:

- Importació de fitxers grib, ja siguin comprimits o no.
- Lectura de fitxers grib de model: Arome, Arpege, Bolam, ECMWF-HRES, ICON, Moloch i WRF.
- Mòduls per a la reprojecció
- Mòduls per al downscaling seguint interpolació bilinear o del veí més proper.