import xarray

def concat_model(model: list, dim: str)-> xarray.DataArray:
    """Takes a list of xarray of a model and concatenate it

    Args:
        model (list): List of models to be concatenated
        dim (str): Dimension over we want to concatenate

    Returns:
        xarray.Datarray: Model concatenated through dim
    """
    # Concatenem el model segons la dimensio "dim"
    model_concat = xarray.concat(model, dim)

    return model_concat


def merge_models(models: list)-> xarray.DataArray:
    """Giving a list of various xarray of data of each
    mode is merged into one Datarray.xarray

    Args:
        models (list): List of xarray.Datarray for each model

    Returns:
        xarray.Datarray: _description_
    """
    model_list=[]
    for model in models:
        # Afegim la coordenada model
        model_new_coord = model.assign_coords(model=model.attrs['model'])
        # La definim com a variable dimensional (varia)
        model_new_coord = model_new_coord.expand_dims('model')
        model_list.append(model_new_coord)

    model_merged = xarray.merge(model_list)

    return model_merged

def hourly_accumulations(model_concat: list):
    """Calculate the hourly accumulations for each model

    Args:
        model_concat (list): list of xarray.Datarray of models.

    Returns:
        xarray.Datarray: hourly acculumation of precipitation
    """
    hourly_data=model_concat.diff('valid_time')
    hourly_data.attrs=model_concat.attrs

    return hourly_data


def export_to_netcdf(file: str, models: list, var: str):
    """Routine which given a list of models and leadtimes
    convert it to a Netcdf to calculate the PME"

    Args:
        file (str):    Path and name of the netcd file where to put the
                       reprojected data.
        models (list): List of models and leadtimes which are the parts 
                       to be used for calculate PME.

        var (str): Variable which will be used.
    """

    to_export = []
    for model in models:
        model_concat=concat_model(model, dim='valid_time')
        if var == 'tp':
            to_export.append(hourly_accumulations(model_concat))

    to_export = merge_models(to_export)

    to_export.to_netcdf(file)

