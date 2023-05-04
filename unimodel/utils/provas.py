import xarray as xr
import numpy as np
import pandas as pd
import rasterio
import shapefile
from shapely.geometry import shape
import json
import rioxarray
import pickle
from cfgrib.xarray_store import open_dataset
import matplotlib.pyplot as plt

from unimodel.io.readers_nwp import read_wrf_prs
from sklearn.neighbors import NearestNeighbors

from unimodel.utils.geotools import reproject_xarray


import shapefile


""" dem_file = 'tests/data/test_data/hres_dem_25831.tif'
da_2t = read_wrf_prs('tests/data/nwp_src/wrf43_prs/WRFPRS-03.2023020600_032.grib', '2t', 'WRF43')

land_binary_mask = read_wrf_prs('tests/data/nwp_src/wrf43_prs/WRFPRS-03.2023020600_032.grib', 'lsm', 'WRF43')
da_orog = read_wrf_prs('tests/data/nwp_src/wrf43_prs/WRFPRS-03.2023020600_032.grib', 'orog', 'WRF43') """

""" with open('tests/data/test_data/var_xarray.pkl', 'wb') as handle:
    pickle.dump([land_binary_mask, da_2t, da_orog], handle)

with open('tests/data/test_data/var_xarray.pkl', 'rb') as file:
    data = pickle.load(file)
    file.close()
 """
""" neigh_candidates = np.where(land_binary_mask == 1)
neigh_candidates = np.vstack((neigh_candidates[1],
                                neigh_candidates[0])).T
neigh_needed = np.where(land_binary_mask >= 0)
neigh_needed = np.vstack((neigh_needed[1],
                            neigh_needed[0])).T

nbrs = NearestNeighbors(n_neighbors=64,
                        algorithm='ball_tree').fit(neigh_candidates)

_, indices = nbrs.kneighbors(neigh_needed)

gradients = np.zeros(da_2t.values.shape)
residues = np.zeros(da_2t.values.shape)

for i, neigh_n in enumerate(neigh_needed):

    idxs = np.hsplit(neigh_candidates[indices[i]], 2)
    
    idx_col = idxs[0].reshape((1, len(idxs[0])))[0]
    idx_row = idxs[1].reshape((1, len(idxs[1])))[0]

    var_sel = da_2t.values[idx_row, idx_col]
    dem_sel = da_orog.values[idx_row, idx_col]
    dem_sel = np.vstack([dem_sel, np.ones(len(dem_sel))]).T

    gradient, residue = np.linalg.lstsq(dem_sel, var_sel, rcond=None)[0]

    gradients[neigh_n[1], neigh_n[0]] = gradient
    residues[neigh_n[1], neigh_n[0]] = residue

gradients[gradients < -0.0098] = -0.0098
gradients[gradients > 0.0294] = 0.0294

xr_gradients = da_2t.copy(data=gradients)

hres_dem = rasterio.open(dem_file)
shape = hres_dem.shape
# ul_corner = (xmin, ymax)
ul_corner = (hres_dem.transform[2], hres_dem.transform[5])
#resolution = (delta_x, delta_y)
resolution = (hres_dem.transform[0], hres_dem.transform[4])
dst_proj = hres_dem.crs

print(da_2t)
print(shape)


hres_2t = reproject_xarray(xr_coarse=da_2t, dst_proj=dst_proj,
                            shape=shape, ul_corner=ul_corner,
                            resolution=resolution)
hres_orog = reproject_xarray(xr_coarse=da_orog, dst_proj=dst_proj,
                                shape=shape, ul_corner=ul_corner,
                                resolution=resolution)
hres_gradients = reproject_xarray(xr_coarse=xr_gradients, dst_proj=dst_proj,
                                    shape=shape, ul_corner=ul_corner,
                                    resolution=resolution)

corrected_field = hres_2t + hres_gradients * hres_orog


 """

""" from shapely.geometry import GeometryCollection, shape

sf = shapefile.Reader('tests/data/coastline/coastline_weurope')

fields = sf.fields[1:]
shapes = sf.shapes()

geometries = []

for shapee in shapes:
    geometry = shapee.__geo_interface__
    shp_geometry = shape(geometry)
    geometries.append(shp_geometry)

geom_collection = GeometryCollection(geometries)

print(geom_collection) """



""" hres_lsm = rasterio.features.rasterize(sf.shape.points,
                                       out_shape=hres_dem.shape,
                                       transform=hres_dem.transform,
                                       all_touched=True) """




# Open the shapefile in read mode
with shapefile.Reader('tests/data/coastline/coastline_weurope') as shp:
    # Get the fields and shapes from the shapefile
    shapes = shp.shapes()

    # Create a list to store the geometries
    geometries = []
    # Loop through each shape and extract its geometry
    for shp_shape in shapes:
        # Extract the geometry from the shape
        geometry = shape(shp_shape.__geo_interface__)
        geometries.append({"geometry": geometry})

    # Convert the list of geometries to a GeoJSON-like dict
    feature_collection = {"type": "FeatureCollection", "features": []}
    for feature in geometries:
        geometry = feature["geometry"]
        feature_dict = {"geometry": json.dumps(geometry.__geo_interface__)}
        feature_collection["features"].append(feature_dict)

# Convert the GeoJSON-like dict to a pandas dataframe
df = pd.json_normalize(feature_collection["features"])

# Convert the "geometry" column to Shapely geometry objects
df["geometry"] = df["geometry"].apply(lambda x: shape(json.loads(x)))

print(df)



dem_file = 'tests/data/test_data/hres_dem_25831.tif'

hres_dem = rasterio.open(dem_file)

hres_lsm = rasterio.features.rasterize(df["geometry"],
                                       out_shape=hres_dem.shape,
                                       transform=hres_dem.transform,
                                       all_touched=True)

# Print the resulting geodataframe
print(hres_lsm.shape)



 