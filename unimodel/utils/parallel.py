from itertools import accumulate

def calc_batch_sizes(n_tasks: int, n_workers: int) -> list:
    """Divide `n_tasks` optimally between n_workers to get batch_sizes.

    Guarantees batch sizes won't differ for more than 1.

    Example:
    # >>>calc_batch_sizes(23, 4)
    # Out: [6, 6, 6, 5]

    In case you're going to use numpy anyway, use np.array_split:
    [len(a) for a in np.array_split(np.arange(23), 4)]
    # Out: [6, 6, 6, 5]
    """
    x = int(n_tasks / n_workers)
    y = n_tasks % n_workers
    batch_sizes = [x + (y > 0)] * y + [x] * (n_workers - y)

    return batch_sizes

def build_batch_ranges(batch_sizes: list) -> list:
    """Build batch_ranges from list of batch_sizes.

    Example:
    # batch_sizes [6, 6, 6, 5]
    # >>>build_batch_ranges(batch_sizes)
    # Out: [range(0, 6), range(6, 12), range(12, 18), range(18, 23)]
    """
    upper_bounds = [*accumulate(batch_sizes)]
    lower_bounds = [0] + upper_bounds[:-1]
    batch_ranges = [range(l, u) for l, u in zip(lower_bounds, upper_bounds)]

    return batch_ranges