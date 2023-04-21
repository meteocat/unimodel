"""Class that calculates the elevation correction of 2t
"""
import os
import numpy as np
import xarray as xr
from sklearn.neighbors import NearestNeighbors

class Ecorrection():
    """Class for applying elevation correction to a given xarray
    """
    def __init__(self, variable: str, config: dict) -> None:
        """Function for checking the input parameters for initializing the object's attributes

        Args:
            variable (str): must be '2t'
            config (dict): configuration dictionary

        Raises:
            ValueError: If variable is not \'2t\' 
            KeyError: If \'hres_dem_file\' not in the configuration dictionary
            FileNotFoundError: If hres_dem_file not found
        """
        if variable != '2t':

            raise ValueError(f'{variable} must be \'2t\'')

        self.variable = variable

        if not config.keys() >= {'hres_dem_file', 'neighbours_file'}:

            raise KeyError('At least \'hres_dem_file\' and \'neighbours_file\' '
                           'must be in the config dictionary')

        self.config = config

        if not os.path.exists(config['hres_dem_file']):

            raise FileNotFoundError(f'{config["hres_dem_file"]} not found')

        self.result = None


    def get_neighbours(self, land_binary_mask: xr.DataArray, out_file: str,
                       neighbours: int=64, save_out: bool=False) -> dict:
        """Function for calculating the nearest neighbours of points to be used in a linear
        regression fitting. Neighbours are selected from those points which 
        landsea_mask is 1. The result is saved in a .npz file

        Args:
            landsea_mask (xarray): NWP landsea mask variable.
            out_file (str): File path where neighbours information is saved
            neighbours (int, optional): Number of neighbours to consider for each
            point. Default is 64.
            save_out (bool, optional): Save neighbours information to a file. 
            Default is False

        Raises:
            ValueError: If \'land_binary_mask\' variable does not exist

        Returns:
            dict: with calculated neighbours information
        """

        if land_binary_mask.attrs['standard_name'] != 'land_binary_mask':

            raise ValueError('\'land_binary_mask\' variable does not exist')

        if not os.path.exists(out_file):

            neigh_candidates = np.where(land_binary_mask == 1)
            neigh_candidates = np.vstack((neigh_candidates[0],
                                          neigh_candidates[1])).T
            neigh_needed = np.where(land_binary_mask >= 0)
            neigh_needed = np.vstack((neigh_needed[0],
                                      neigh_needed[1])).T

            nbrs = NearestNeighbors(n_neighbors=neighbours,
                                    algorithm='ball_tree').fit(neigh_candidates)

            _, indices = nbrs.kneighbors(neigh_needed)

            if save_out:

                np.savez_compressed(out_file,
                                    indices=indices,
                                    neigh_needed=neigh_needed,
                                    neigh_candidates=neigh_candidates)

            neigh_summary = {'indices': indices,
                             'neigh_needed': neigh_needed, 
                             'neigh_candidates': neigh_candidates}

        else:

            out_data = np.load(out_file)

            indices = out_data['indices']
            neigh_needed = out_data['neigh_needed']
            neigh_candidates = out_data['neigh_candidates']

            neigh_summary = {'indices': indices,
                             'neigh_needed': neigh_needed, 
                             'neigh_candidates': neigh_candidates}

        return neigh_summary

    def calculate_lapse_rate(self, neigh_info: dict,
                             da_2t: xr.DataArray, da_h: xr.DataArray) -> tuple:
        """Calculates the lapse rates for each WRF pixel from a mask_file,
        which includes the nearest neighbors for each pixel. Only pixels
        with the aid of WRF LANDMASK value of 1 are considered.

        Args:
            neigh_info (dict): Dictionary with info about neighbours.
            da_2t (xarray.DataArray): 2t variable DataArray
            da_h (xarray.DataArray): height variable DataArray

        Returns:
            numpy.arrays: Two arrays with gradients and residues from linear
            regression calculations.
        """

        if neigh_info.keys() != {'indices', 'neigh_needed', 'neigh_candidates'}:

            raise KeyError("'indices', 'neigh_needed' and 'neigh_candidates' "
                           "must be in the neigh_info dictionary")

        if da_2t.attrs['GRIB_cfVarName'] != 't2m':

            raise ValueError('2t variable does not exist')

        if da_h.attrs['GRIB_shortName'] != 'ghrea':

            raise ValueError('height variable does not exist')

        indices = neigh_info['indices']
        neigh_candidates = neigh_info['neigh_candidates']
        neigh_needed = neigh_info['neigh_needed']

        gradients = np.ones(nwp_var.shape)
        residues = np.zeros(nwp_var.shape)
        for i, neigh_n in enumerate(neigh_needed):
            idxs = np.hsplit(neigh_candidates[indices[i]], 2)
            idx_row = idxs[0].reshape((1, len(idxs[0])))[0]
            idx_col = idxs[1].reshape((1, len(idxs[1])))[0]

            var_sel = nwp_var.values[idx_row, idx_col]
            dem_sel = nwp_dem.values[idx_row, idx_col]
            dem_sel = np.vstack([dem_sel, np.ones(len(dem_sel))]).T

            gradient, residue = np.linalg.lstsq(dem_sel, var_sel, rcond=None)[0]

            gradients[neigh_n[0], neigh_n[1]] = gradient
            residues[neigh_n[0], neigh_n[1]] = residue

        gradients[gradients == 1] = 0
        gradients[gradients < -0.0098] = -0.0098
        gradients[gradients > 0.0294] = 0.0294

        xr_gradients = nwp_var.copy(data=gradients)
        xr_residues = nwp_var.copy(data=residues)

        return xr_gradients, xr_residues

