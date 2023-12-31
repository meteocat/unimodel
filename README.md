[![Anaconda-Server Badge](https://anaconda.org/meteocat/unimodel/badges/version.svg)](https://anaconda.org/meteocat/unimodel)
[![Documentation Status](https://readthedocs.org/projects/unimodel/badge/?version=latest)](https://unimodel.readthedocs.io/en/latest/?badge=latest)


<img src="docs/source/_static/img/logo_unimodel_trans.png" alt="logo" width="250"/>

Aquest paquet de Python implementa un seguit de mòduls per llegir i facilitar el processament
de les sortides dels models de prediccó numèrica del temps en format grib disponibles al
Servei Meteorològic de Catalunya. Els mòduls llegeixen els fitxers grib i els transformen en
`xarray.DataArray`, que inclouen les dades, la projecció i les coordenades en la projecció
nativa del grib.

A part, el paquet inclou també un mòdul d'interpolació i reprojecció dels `xarray.DataArray`. Les
metodologies d'interpolació que hi ha implementades són, de moment, *nearest* i *bilinear*. La
reprojecció es fa mitjançant la llibreria `rioxarray`. Els mòduls d'interpolació poden incloure també,
de forma opcional, una reprojecció.

A més, s'inclou també un mòdul de refinament del camp de temperatura basat en les diferències d'altitud
que hi ha entre l'orografia del model i la d'un model digital d'elevació de més resolució espacial.

La sortida per defecte de la lectura dels models és un `xarray.DataArray`, però s'inclou un mòdul per
exportar les dades en format netCDF. L'exportació és d'un únic `xarray.DataArray` que pot incloure més
d'un horitzó de pronòstic i més d'un model.

Instal·lació
------------

El paquet es troba al canal meteocat de `conda` i es pot instal·lar mitjançant:

`conda install -c conda-forge -c meteocat unimodel`

També es pot instal·lar de la manera tradicional utilitzant `pip`. En primer lloc, cal crear un entorn
`conda` amb les llibreries necessàries per executar correctament el paquet. Aquetes es poden trobar dins del fitxer
`unimodel_environment.yml`.

`conda env create -f unimodel_environment.yml`

Una vegada activat l'entorn `conda`, la instal·lació del paquet es pot fer a partir de la comanda
següent:

`pip install [path a la carpeta unimodel]`

Coverage
--------

Per avaluar la cobertura dels testos s'ha d'executar la comanda següent:

`pytest --cov=./unimodel ./tests --cov-report=xml:cov.xml`