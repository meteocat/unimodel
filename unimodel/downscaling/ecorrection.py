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