"""Class that calculates the elevation correction of 2t"""

import os

import numpy as np
import rasterio
import rasterio.fill
import xarray as xr
from sklearn.neighbors import NearestNeighbors

from unimodel.utils.geotools import landsea_mask_from_shp, reproject_xarray
from unimodel.utils.numba_tools import linalg_lstsq


class Ecorrection:
    """Class for applying elevation correction to a given xarray"""

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
        if land_binary_mask.attrs["standard_name"] != "land_binary_mask":
            raise ValueError("'land_binary_mask' dataArray does not exist")

        # Values greater than 0.5 are considered land
        land_binary_mask.data = np.where(land_binary_mask.data > 0.5, 1, 0)
        self.land_binary_mask = land_binary_mask

        self.neigh_info = self.__calculate_neighbours(land_binary_mask)

        if not os.path.exists(dem_file):
            raise FileNotFoundError("dem_file not found")

        self.dem_file = dem_file

        self.hres_lsm = None

        self.result = None

    def __calculate_neighbours(
        self, land_binary_mask: xr.DataArray, neighbours: int = 64
    ) -> dict:
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
        neigh_candidates = np.vstack((neigh_candidates[1], neigh_candidates[0])).T
        neigh_needed = np.where(land_binary_mask >= 0)
        neigh_needed = np.vstack((neigh_needed[1], neigh_needed[0])).T

        nbrs = NearestNeighbors(n_neighbors=neighbours, algorithm="ball_tree").fit(
            neigh_candidates
        )

        _, indices = nbrs.kneighbors(neigh_needed)

        neigh_summary = {
            "indices": indices,
            "neigh_needed": neigh_needed,
            "neigh_candidates": neigh_candidates,
        }

        return neigh_summary

    def calculate_lapse_rate(
        self, da_2t: xr.DataArray, da_orog: xr.DataArray
    ) -> xr.DataArray:
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
        indices = self.neigh_info["indices"]
        neigh_candidates = self.neigh_info["neigh_candidates"]

        neigh_candidates = neigh_candidates[indices]
        idx_col = neigh_candidates[:, :, 0].ravel()
        idx_row = neigh_candidates[:, :, 1].ravel()

        var_sel = da_2t.values[idx_row, idx_col].reshape(-1, len(indices[0]))
        dem_sel = da_orog.values[idx_row, idx_col].reshape(-1, len(indices[0]))

        # Apply the least-squares method
        _, gradients = linalg_lstsq(dem_sel, var_sel)

        # Set upper- and lower-limits
        gradients[gradients < -0.0098] = -0.0098
        gradients[gradients > 0.0294] = 0.0294

        gradients = gradients.reshape(da_2t.data.shape)

        xr_gradients = da_2t.copy(data=gradients)

        return xr_gradients

    def apply_correction(
        self, da_2t: xr.DataArray, da_orog: xr.DataArray, lsm_shp: str = None
    ) -> xr.DataArray:
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
        if da_2t.attrs["GRIB_shortName"] != "2t":
            raise ValueError("2t variable does not exist")

        if da_orog.attrs["GRIB_shortName"] not in ["orog", "mterh", "h", "HSURF"]:
            raise ValueError(
                "orography variable names supported: 'orog',"
                " 'mterh', 'h' and 'HSURF'"
            )

        gradients = self.calculate_lapse_rate(da_2t, da_orog)

        hres_dem = rasterio.open(self.dem_file)
        shape = hres_dem.shape
        ul_corner = (hres_dem.transform[2], hres_dem.transform[5])
        resolution = (hres_dem.transform[0], abs(hres_dem.transform[4]))
        dst_proj = hres_dem.crs

        hres_2t = reproject_xarray(
            xr_coarse=da_2t,
            dst_proj=dst_proj,
            shape=shape,
            ul_corner=ul_corner,
            resolution=resolution,
        )
        hres_orog = reproject_xarray(
            xr_coarse=da_orog,
            dst_proj=dst_proj,
            shape=shape,
            ul_corner=ul_corner,
            resolution=resolution,
        )
        hres_gradients = reproject_xarray(
            xr_coarse=gradients,
            dst_proj=dst_proj,
            shape=shape,
            ul_corner=ul_corner,
            resolution=resolution,
        )

        if lsm_shp is not None:
            # If lsm from shapefile is not yet calculated
            if self.hres_lsm is None:
                self.hres_lsm = landsea_mask_from_shp(hres_dem, lsm_shp)

            # Select only data over land
            var_2t = da_2t * self.land_binary_mask
            # Data over sea redefine as NoData
            var_2t.attrs["_FillValue"] = 0

            # Reproject data that is only over land
            hres_2t_mask = reproject_xarray(
                xr_coarse=var_2t,
                dst_proj=dst_proj,
                shape=shape,
                ul_corner=ul_corner,
                resolution=resolution,
            )

            # Fill NoData (sea) with the surrounding data (land),
            # up to 50 pixels (from the coastline)
            hres_2t_mask.values = rasterio.fill.fillnodata(
                hres_2t_mask.values, hres_2t_mask.values, max_search_distance=50
            )

            # Fill the new hres data (with new lsm=1 values) with surrounding
            # data
            hres_2t.values = np.where(
                self.hres_lsm == 1, hres_2t_mask.values, hres_2t.values
            )

        # Apply correction
        corrected_field = hres_2t + hres_gradients * (hres_dem.read(1) - hres_orog)

        if hres_2t.units == "K":
            corrected_field = corrected_field - 273.15

        return corrected_field
