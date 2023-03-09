"""Module to export xarray to different file formats.
"""
import xarray

from unimodel.utils.decorators import xarray_attributes


@xarray_attributes
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


@xarray_attributes
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

    run_date = str(diff_data.time.dt.strftime("%Y-%m-%d %H:%M:%S").data)
    diff_data.valid_time.encoding['units'] = "hours since " + run_date

    return diff_data


def concat_and_merge(models: list) -> xarray.DataArray:
    """Concats and mergres a list of model lists to a single xarray.Datarray.
    If model variable is 'tp' `differences_by_lead_time` is applied."

    Args:
        models (list): List of xarray.DataArray model lists. Elements of the
                       parent list correspond to different models, and elements
                       of the child list to different lead times
                       (i.e [[arome_lt0, arome_lt1, ...], [arpege_lt0,
                       arpege_lt1, ...]]).
    Returns:
        xarray: Concatenated and merged models.
    """
    
    data_xarray = []
    for model in models:
        model_concat = concat_model(model, dim='valid_time')
        if model_concat.name == 'tp':
            data_xarray.append(differences_by_lead_time(model_concat))
        else:
            data_xarray.append(model_concat)

    data_xarray = merge_models(data_xarray)

    return data_xarray

    
