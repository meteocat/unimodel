Instal·lació
============

Per poder executar correctament el paquet, cal primer disposar d'un entorn conda. Aquest
es pot crear de nou a través de la següent comanda:

``conda env create -n unimodel -f unimodel_environment.yml``

O bé, en un entorn conda ja creat, tenir en compte que el paquet **unimodel** necessitarà:

- cfgrib
- eccodes
- netcdf4
- pyproj
- rioxarray
- xarray
- shapely
- pyshp
- scikit-learn
- numba

Per ara, aquest paquet es pot instal·lar de la forma tradicional amb pip i a través de conda.

anaconda
--------

El paquest **unimodel** es troba al distribuidor Anaconda i es pot insta·lar amb la següent comanda:

``conda install -c meteocat -c conda-forge unimodel``

pip
---

Tot i que l'**unimodel** no es troba encara al distribuïdor de paquets Pypi, sí que es pot
instal·lar a partir de la següent comanda.

``pip install [unimodel path]``


setup.py
--------

També es pot instal·lar seguint la metodologia tradicional a través de la següent comanda.

``python setup.py install``
