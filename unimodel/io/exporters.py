"""Module to export xarray to different file formats.
"""
import xarray


def concat_model(model: list, dim: str) -> xarray.DataArray:
    """Concatenates a list of model xarrays.

    Args:
        model (list): List of models xarrays.
        dim (str): Dimension over we want to concatenate

    Returns:
        xarray.Datarray: Model concatenated.
    """
    model_concat = xarray.concat(model, dim)

    return model_concat


def merge_models(models: list) -> xarray.DataArray:
    """
    Merges a list of different model xarray.DataArray into a single
    xarray.DataArray with a new dimension named 'model'.

    Args:
        models (list): List of models xarray.DataArray.

    Returns:
        xarray.Datarray: Merged data with new dimension 'model'.
    """
    model_list = []
    for model in models:
        # Add 'model' coordinate
        model_new_coord = model.assign_coords(model=model.attrs['model'])
        # New coordinate 'model' as dimension
        model_new_coord = model_new_coord.expand_dims('model')
        model_list.append(model_new_coord)

    model_merged = xarray.merge(model_list)

    return model_merged


def differences_by_lead_time(model_concat: list) -> xarray.DataArray:
    """Iteratively calculates the differences between the current lead time
    and the previous. The 'upper' label of the difference is considered, that
    is, (lt=1 - lt=0) -> lt=1.

    Args:
        model_concat (list): List of xarray.DataArray of a single model with
                             different lead times.

    Returns:
        xarray.Datarray: Iterative differences between lead times.
    """
    diff_data = model_concat.diff('valid_time')
    diff_data.attrs = model_concat.attrs

    return diff_data


def export_to_netcdf(models: list, out_file: str):
    """Export a lists of model lists to netCDF."

    Args:
        models (list): List of xarray.DataArray model lists. Elements of the
                       parent list correspond to different models, and elements
                       of the child list to different lead times
                       (i.e [[arome_lt0, arome_lt1, ...], [arpege_lt0,
                       arpege_lt1, ...]]).
        out_file (str): Output file path where model data are to be saved.
    """
    to_export = []
    for model in models:
        model_concat = concat_model(model, dim='valid_time')
        if model_concat.name == 'tp':
            to_export.append(differences_by_lead_time(model_concat))
        else:
            to_export.append(model_concat)

    if to_export[0].name == 'tp':
        to_export = merge_models(to_export)
        # Change units of 'valid_time' to NWP model run date
        run_date = str(to_export.time.dt.strftime("%Y-%m-%d %H:%M:%S").data)
        to_export.valid_time.encoding['units'] = "hours since " + run_date
    else:
        to_export = merge_models(to_export)

    to_export.to_netcdf(out_file)
