"""Unimodel custom error messages.
"""


def raise_reader_missing_filters(grib_file, variable, model, error):
    """Raises a custom TypeError message to modify the cfgrib message when there are
    multiple values for a unique key needed

    Args:
        grib_file (str): Path to the grib file.
        variable (string): Variable to extract.
        model (str): Model to read.
        error (cfgrib.dataset.DatasetBuildError): Original exception.

    Raises:
        TypeError: Customized exception.
    """
    default_error = str(error)
    error_filter = default_error.replace("filter_by_keys", "extra_filters")
    error_variable = error_filter.replace(f", 'shortName': '{variable}'", "")
    error_filter_1 = [line.strip() for line in error_variable.splitlines()][-1]
    error_example = (
        f"\nFor example:\n reader(grib_file='{grib_file}', "
        f"variable='{variable}', model='{model}', {error_filter_1})"
    )
    raise_error = "The grib file has " + error_variable + error_example

    raise TypeError(raise_error) from None
