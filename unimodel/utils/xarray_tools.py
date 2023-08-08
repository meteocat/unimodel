"""Module with xarray tools."""
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import xarray


def expand_valid_time_coord(
    data: xarray.DataArray, lead_time: int, interval: int
) -> xarray.DataArray:
    """Expands time coordinate of an xarray.DataArray to specified forecast
    lead time (hours) by a specified interval (hours) using np.nan as
    FillValue.

    Args:
        data (xarray.DataArray): xarray.DataArray to be padded.
        lead_time (int): Forecast lead time which data is padded to.
        interval (int): Time resolution (in hours).

    Raises:
        KeyError: If coordinate 'time' not in data.
        ValueError: If 'interval' is different than temporal resolution
                    of data.
        ValueError: If 'lead_time' is not a multiple of 'interval'.

    Returns:
        xarray.DataArray: Padded data to specified lead time and time
                          resolution.
    """
    if "valid_time" not in data.coords:
        raise KeyError("'valid_time' not in data coordinates.")

    time_coord = data.valid_time.values
    # If time_coord is a single value, transform it into a list
    if not isinstance(data.valid_time.values, np.ndarray):
        time_coord = [time_coord]
    # Otherwise, check if 'interval' is coherent with temporal resolution of
    # data
    else:
        data_interval = (data.step[1] - data.step[0]) / 1e9 / 3600
        if data_interval != interval:
            raise ValueError(
                "'interval' is different than temporal resolution of data."
            )
    # Transform time_coord to datetime format
    time_coord = [datetime.utcfromtimestamp(dt.astype(int) / 1e9) for dt in time_coord]

    start_date_pad = time_coord[-1]
    end_date_pad = time_coord[0] + timedelta(hours=lead_time)

    # If valid_time coordinate is not a dimension
    if not data.valid_time.shape:
        data = data.expand_dims(dim={"valid_time": [start_date_pad]})

    # Check if 'lead_time' is a multiple of 'interval'
    if np.mod((end_date_pad - start_date_pad).total_seconds() / 3600, interval) == 0:
        num_pad = (
            int(((end_date_pad - start_date_pad).total_seconds() / 3600) / interval) - 1
        )
    else:
        raise ValueError(
            "'lead_time' is not a multiple of 'interval'. "
            "Padding of xarray is discarded."
        )

    # Define new valid_time coordinate
    valid_time_coord = pd.date_range(
        start=time_coord[0],
        end=end_date_pad,
        freq=str(interval) + "H",
        inclusive="left",
    )

    # Expand valid_time dimension
    data = data.pad(valid_time=(0, num_pad), constant_values=np.nan)
    # Assign new valid_time coordinates to data
    data = data.assign_coords({"valid_time": valid_time_coord})

    return data
