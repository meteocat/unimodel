Control de versions
===================

v0.1.0 - 28/03/2023
-------------------

Aquesta nova versió incorpora els següents canvis:

- Lectura dels fitxers de l'Unified Model (UM) mitjançant la funció :py:func:`unimodel.io.readers_nwp.read_unified_model_grib`.
- Lectura dels fitxers del time-lagged ensemble del WRF (WRF-TL-ENS) mitjançant 
la funció :py:func:`unimodel.io.readers_nwp.read_wrf_tl_ens_grib`.
- Funció que permet allargar l'hortizó de pronòstic d'un model amb un valor constant de ``np.nan``.

v0.0.0 - 06/03/2023
-------------------

Primera versió operativa del paquet de Python **unimodel**. Aquesta inclou:

- Importació de fitxers grib, ja siguin comprimits o no.
- Lectura de fitxers grib de model: Arome, Arpege, Bolam, ECMWF-HRES, ICON, Moloch i WRF.
- Mòduls per a la reprojecció
- Mòduls per al downscaling seguint interpolació bilinear o del veí més proper.