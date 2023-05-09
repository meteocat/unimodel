.. unimodel documentation master file, created by
   sphinx-quickstart on Thu Mar  9 07:34:35 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

unimodel
========

Aquest paquet de Python implementa un seguit de mòduls per llegir i facilitar el processament
de les sortides dels models de prediccó numèrica del temps en format grib disponibles al
Servei Meteorològic de Catalunya. Els mòduls llegeixen els fitxers grib i els transformen en
`xarray.DataArray`, que inclouen les dades, la projecció i les coordenades en la projecció
nativa del grib.

A part, el paquet inclou també un mòdul d'interpolació i reprojecció dels `xarray.DataArray`. Les
metodologies d'interpolació que hi ha implementades són, de moment, *nearest* i *bilinear*. La
reprojecció es fa mitjançant la llibreria rioxarray. Els mòduls d'interpolació poden incloure també,
de forma opcional, una reprojecció.

La sortida per defecte de la lectura dels models és un `xarray.DataArray`. S'inclou un mòdul per
treballar amb els `xarray.DataArray` resultants i agrupar-los per horitzó de pronòstic i model. Així,
l'`xarray.DataArray` pot incloure més d'un horitzó de pronòstic i més d'un model.

.. toctree::
   :maxdepth: 2
   :caption: Continguts:

   installation
   howto
   downscaling
   api
   vcontrol


Índexs i taules
===============

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
