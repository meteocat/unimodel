"""Class that calculates the elevation correction of 2t
"""
import os
import numpy as np
import xarray as xr
import rasterio
from sklearn.neighbors import NearestNeighbors

from unimodel.utils.geotools import reproject_xarray

class Ecorrection():
    """Class for applying elevation correction to a given xarray
    """
    def __init__(self, land_binary_mask: xr.DataArray, dem_file: str) -> None:
        """Function for initializing the object's attributes

        Args:
            land_binary_mask (xarray): NWP landsea mask variable
            dem_file (str): path to hres_dem_file

        Raises:
            ValueError: If 'land_binary_mask' DataArray does not exist
            KeyError: If 'indices', 'neigh_needed' and 'neigh_candidates' are not dict keys
            FileNotFoundError: If hres_dem_file not found
        """

        if land_binary_mask.attrs['standard_name'] != 'land_binary_mask':

            raise ValueError("'land_binary_mask' dataArray does not exist")

        self.land_binary_mask = land_binary_mask

        neigh_info = self.__calculate_neighbours(land_binary_mask)

        if neigh_info.keys() != {'indices', 'neigh_needed', 'neigh_candidates'}:

            raise KeyError("'indices', 'neigh_needed' and 'neigh_candidates' "
                           "must be in the neigh_info dictionary")

        self.neigh_info = neigh_info

        if not os.path.exists(dem_file):

            raise FileNotFoundError('dem_file not found')

        self.result = None


    def __calculate_neighbours(self, land_binary_mask: xr.DataArray, neighbours: int=64) -> dict:
        """Function for calculating the nearest neighbours of points to be used in a linear
        regression fitting. Neighbours are selected from those points which 
        landsea_mask is 1.

        Args:
            landsea_mask (xarray): NWP landsea mask variable.
            neighbours (int, optional): Number of neighbours to consider for each
            point. Default is 64.

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

    def calculate_lapse_rate(self, da_2t: xr.DataArray, da_orog: xr.DataArray) -> xr.DataArray:
        """Calculates the lapse rates for each WRF pixel from a mask_file,
        which includes the nearest neighbors for each pixel. Only pixels
        with the aid of WRF LANDMASK value of 1 are considered.

        Args:
            neigh_info (dict): Dictionary with info about neighbours.
            da_2t (xarray.DataArray): 2t variable DataArray
            da_orog (xarray.DataArray): orography variable DataArray

        Returns:
            numpy.arrays: Two arrays with gradients and residues from linear
            regression calculations.
        """

        if da_2t.attrs['GRIB_shortName'] != '2t':

            raise ValueError('2t variable does not exist')

        if da_orog.attrs['GRIB_shortName'] != 'orog':

            raise ValueError('orography variable does not exist')

        indices = self.neigh_info['indices']
        neigh_candidates = self.neigh_info['neigh_candidates']
        neigh_needed = self.neigh_info['neigh_needed']

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

        return xr_gradients


    def apply_correction(self, dem_file: str, da_2t: xr.DataArray,
                         da_orog: xr.DataArray) -> xr.DataArray:
        """Apply the elevation correction of 2t field.

        Args:
            dem_file (str): path to hres_dem_file
            da_2t (xarray.DataArray): 2t variable DataArray
            da_orog (xarray.DataArray): orography variable DataArray

        Raises:
            ValueError: If '2t' DataArray does not exist
            ValueError: If 'orography' DataArray does not exist

        Returns:
            xr.DataArray: DataArray with field corrected
        """

        if da_2t.attrs['GRIB_shortName'] != '2t':

            raise ValueError('2t variable does not exist')

        if da_orog.attrs['GRIB_shortName'] != 'orog':

            raise ValueError('orography variable does not exist')

        gradients = self.calculate_lapse_rate(da_2t, da_orog)

        hres_dem = rasterio.open(dem_file)
        shape = hres_dem.shape
        # ul_corner = (xmin, ymax)
        ul_corner = (hres_dem.transform[2], hres_dem.transform[5])
        #resolution = (delta_x, delta_y)
        resolution = (hres_dem.transform[0], hres_dem.transform[4])


        hres_2t = reproject_xarray(xr_coarse=da_2t, dst_proj=hres_dem,
                                   shape=shape, ul_corner=ul_corner,
                                   resolution=resolution)
        hres_orog = reproject_xarray(xr_coarse=da_orog, dst_proj=hres_dem,
                                     shape=shape, ul_corner=ul_corner,
                                     resolution=resolution)
        hres_gradients = reproject_xarray(xr_coarse=gradients, dst_proj=hres_dem,
                                          shape=shape, ul_corner=ul_corner,
                                          resolution=resolution)

        corrected_field = hres_2t + hres_gradients * (hres_dem - hres_orog) - 273.15

        return corrected_field
    