"""Class that calculates the elevation correction of 2t
"""
import os
import numpy as np
import xarray as xr
import rasterio
import rasterio.fill
from sklearn.neighbors import NearestNeighbors


import functools
from multiprocessing import Pool

import time

from unimodel.utils.geotools import reproject_xarray, landsea_mask_from_shp
from unimodel.utils.parallel import calc_batch_sizes, build_batch_ranges


class Ecorrection():
    """Class for applying elevation correction to a given xarray
    """
    def __init__(self, land_binary_mask: xr.DataArray, dem_file: str) -> None:
        """Function for initializing the object's attributes.

        Args:
            land_binary_mask (xarray): NWP landsea mask variable.
            dem_file (str): path to hres_dem_file.

        Raises:
            ValueError: If 'land_binary_mask' DataArray does not exist.
            KeyError: If 'indices', 'neigh_needed' and 'neigh_candidates' are
                      not dict keys.
            FileNotFoundError: If hres_dem_file not found.
        """
        if land_binary_mask.attrs['standard_name'] != 'land_binary_mask':

            raise ValueError("'land_binary_mask' dataArray does not exist")

        # Values greater than 0.5 are considered land
        land_binary_mask.data = np.where(land_binary_mask.data > 0.5, 1, 0)
        self.land_binary_mask = land_binary_mask

        self.neigh_info = self.__calculate_neighbours(land_binary_mask)

        if not os.path.exists(dem_file):
            raise FileNotFoundError('dem_file not found')

        self.dem_file = dem_file

        self.result = None

    def __calculate_neighbours(self, land_binary_mask: xr.DataArray,
                               neighbours: int = 64) -> dict:
        """Calculates the nearest neighbours of points to be used in a linear
        regression fitting. Neighbours are selected from those points which
        landsea_mask is 1.

        Args:
            landsea_mask (xarray): NWP landsea mask variable.
            neighbours (int, optional): Number of neighbours to consider for
                                        each point. Default is 64.

        Returns:
            dict: with calculated neighbours information
        """
        neigh_candidates = np.where(land_binary_mask == 1)
        neigh_candidates = np.vstack((neigh_candidates[1],
                                      neigh_candidates[0])).T
        neigh_needed = np.where(land_binary_mask >= 0)
        neigh_needed = np.vstack((neigh_needed[1],
                                  neigh_needed[0])).T

        nbrs = NearestNeighbors(n_neighbors=neighbours,
                                algorithm='ball_tree').fit(neigh_candidates)

        _, indices = nbrs.kneighbors(neigh_needed)

        neigh_summary = {'indices': indices,
                         'neigh_needed': neigh_needed,
                         'neigh_candidates': neigh_candidates}

        return neigh_summary

    def regression(self, batch_ranges, neigh_needed, gradients,
                   neigh_candidates, indices, da_2t, da_orog):
    
        neigh_to_calculate = neigh_needed[batch_ranges]
        for i, neigh_n in enumerate(neigh_to_calculate):
            idxs = np.hsplit(neigh_candidates[indices[batch_ranges[0]+i]], 2)
            idx_col = idxs[0].reshape((1, len(idxs[0])))[0]
            idx_row = idxs[1].reshape((1, len(idxs[1])))[0]

            var_sel = da_2t.values[idx_row, idx_col]
            dem_sel = da_orog.values[idx_row, idx_col]
            dem_sel = np.vstack([dem_sel, np.ones(len(dem_sel))]).T

            # Apply the least-squares method
            gradient, _ = np.linalg.lstsq(dem_sel, var_sel, rcond=None)[0]

            gradients[neigh_n[1], neigh_n[0]] = gradient
        
        return gradients
        


    def calculate_lapse_rate(self, da_2t: xr.DataArray,
                             da_orog: xr.DataArray) -> xr.DataArray:
        
        """Calculates the lapse rates for each WRF pixel selecting the nearest
        neighbors for each pixel. Only pixels where  WRF LANDMASK value equals
        1 are considered, those that are over land.

        Args:
            neigh_info (dict): Dictionary with info about neighbours.
            da_2t (xarray.DataArray): 2t variable DataArray
            da_orog (xarray.DataArray): orography variable DataArray

        Returns:
            numpy.arrays: Two arrays with gradients and residues from linear
            regression calculations.
        """
        indices = self.neigh_info['indices']
        neigh_candidates = self.neigh_info['neigh_candidates']
        neigh_needed = self.neigh_info['neigh_needed']

        gradients = np.zeros(da_2t.values.shape)

        n_tasks = len(neigh_needed)
        n_workers = 4
        batch_sizes = calc_batch_sizes(n_tasks, n_workers)
        batch_ranges = build_batch_ranges(batch_sizes)

        with Pool(n_workers) as pool:
            partial_regression = functools.partial(self.regression,
                                                   neigh_needed=neigh_needed, gradients=gradients,
                                                   neigh_candidates=neigh_candidates,
                                                   indices=indices,da_2t=da_2t, da_orog=da_orog)
            partial_gradient = pool.map(partial_regression, batch_ranges)


        gradient = np.sum(partial_gradient, axis=0)

        # Set upper- and lower-limits
        gradient[gradient < -0.0098] = -0.0098
        gradient[gradient > 0.0294] = 0.0294

        xr_gradients = da_2t.copy(data=gradient)

        return xr_gradients

        
    def apply_correction(self, da_2t: xr.DataArray, da_orog: xr.DataArray,
                         lsm_shp: str = None) -> xr.DataArray:
        """Apply the elevation correction of 2t field.

        Args:
            da_2t (xarray.DataArray): 2t variable DataArray
            da_orog (xarray.DataArray): orography variable DataArray
            lsm_shp (str, optional): If not None reprojection to destination
                                        resolution is done accounting for
                                        landsea mask values. Defaults to None.

        Raises:
            ValueError: If '2t' DataArray does not exist
            ValueError: If 'orography' DataArray does not exist

        Returns:
            xr.DataArray: DataArray with field corrected
        """
        if da_2t.attrs['GRIB_shortName'] != '2t':
            raise ValueError('2t variable does not exist')

        if da_orog.attrs['GRIB_shortName'] not in ['orog', 'mterh',
                                                   'h', 'HSURF']:
            raise ValueError("orography variable names supported: 'orog',"
                             " 'mterh', 'h' and 'HSURF'")

        gradients = self.calculate_lapse_rate(da_2t, da_orog)

        hres_dem = rasterio.open(self.dem_file)
        shape = hres_dem.shape
        ul_corner = (hres_dem.transform[2], hres_dem.transform[5])
        resolution = (hres_dem.transform[0], abs(hres_dem.transform[4]))
        dst_proj = hres_dem.crs

        hres_2t = reproject_xarray(xr_coarse=da_2t, dst_proj=dst_proj,
                                   shape=shape, ul_corner=ul_corner,
                                   resolution=resolution)
        hres_orog = reproject_xarray(xr_coarse=da_orog, dst_proj=dst_proj,
                                     shape=shape, ul_corner=ul_corner,
                                     resolution=resolution)
        hres_gradients = reproject_xarray(xr_coarse=gradients,
                                          dst_proj=dst_proj,
                                          shape=shape, ul_corner=ul_corner,
                                          resolution=resolution)

        if lsm_shp is not None:
            hres_lsm = landsea_mask_from_shp(hres_dem, lsm_shp)

            # Select only data over land
            var_2t = da_2t * self.land_binary_mask
            # Data over sea redefine as NoData
            var_2t.attrs['_FillValue'] = 0

            # Reproject data that is only over land
            hres_2t_mask = reproject_xarray(xr_coarse=var_2t,
                                            dst_proj=dst_proj,
                                            shape=shape,
                                            ul_corner=ul_corner,
                                            resolution=resolution)

            # Fill NoData (sea) with the surrounding data (land),
            # up to 50 pixels (from the coastline)
            hres_2t_mask.values = rasterio.fill.fillnodata(
                hres_2t_mask.values, hres_2t_mask.values,
                max_search_distance=50)

            # Fill the new hres data (with new lsm=1 values) with surrounding
            # data
            hres_2t.values = np.where(hres_lsm == 1, hres_2t_mask.values,
                                      hres_2t.values)

        # Apply correction
        corrected_field = hres_2t + hres_gradients * (hres_dem.read(1) -
                                                      hres_orog)

        if hres_2t.units == 'K':
            corrected_field = corrected_field - 273.15

        return corrected_field
