import numba
import numpy as np


@numba.jit(nogil=True, parallel=True, nopython=True)
def linalg_lstsq(XX, yy):
    """Fit a large set of points to a regression"""
    assert XX.shape == yy.shape, "Inputs mismatched"
    n_pnts, _ = XX.shape

    scale = np.empty(n_pnts)
    offset = np.empty(n_pnts)

    for i in numba.prange(n_pnts):
        X, y = XX[i], yy[i]
        A = np.vstack((np.ones_like(X), X)).T
        offset[i], scale[i] = np.linalg.lstsq(A, y)[0]

    return offset, scale
