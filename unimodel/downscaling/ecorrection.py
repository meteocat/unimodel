import os
import numpy as np
import xarray as xr
from sklearn.neighbors import NearestNeighbors

class Ecorrection():

    def __init__(self, variable: str, config: dict) -> None:
        
        if variable != '2t':

            raise ValueError(f'{variable} must be \'2t\'')
        
        self.variable = variable

        if not config.keys() <= {'hres_dem_file', 'neighbours_file'}:

            raise KeyError(f'At least \'hres_dem_file\' and \'neighbours_file\' must be in the config dictionary')
        
        self.config = config

        if not os.path.exists(config['hres_dem_file']):

            raise FileNotFoundError(f'{config["hres_dem_file"]} not found')
        
        self.result = None

    def __get_neighbours(land_binary_mask: xr.Dataset, out_file: str, neighbours: int):

        try:

            if not os.path.exists(out_file):

                neigh_candidates = np.where(land_binary_mask == 1)
                neigh_candidates = np.vstack((neigh_candidates[0], neigh_candidates[1])).T
                neigh_needed = np.where(land_binary_mask >= 0)
                neigh_needed = np.vstack((neigh_needed[0], neigh_needed[1])).T

                nbrs = NearestNeighbors(n_neighbors=neighbours, algorithm='ball_tree').fit(neigh_candidates)
                _, indices = nbrs.kneighbors(neigh_needed)

                np.savez_compressed(out_file,
                                    indices=indices,
                                    neigh_needed=neigh_needed,
                                    neigh_candidates=neigh_candidates)
                
                neigh_summary = {'indices': indices, 'neigh_neeed': neigh_needed, 'neigh_candidates': neigh_candidates}
            
            return neigh_summary
            
        except Exception:

            raise NameError(f'\'land_binary_mask\' variable not defined')

