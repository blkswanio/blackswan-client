import pandas as pd
import numpy as np
from datetime import datetime as dt
import operator as op
import multiprocessing as mp


def ncr(n, r):
    # Source: https://stackoverflow.com/questions/4941753/is-there-a-math-ncr-function-in-python
    r = min(r, n-r)
    if r == 0: return 1
    numer = reduce(op.mul, xrange(n, n-r, -1))
    denom = reduce(op.mul, xrange(1, r+1))
    return numer//denom


def column2val(df, column):
    """ For a given dataframe and column name, return the only unique value in the column;
     If there are multiple unique values, print an error and return the first one.
    """
    vals = df[column].unique()
    if len(vals) == 1:
        return vals[0]
    else:
        return vals


def median_and_ci(s):
    """ For a value series (or dataframe column), return median and median CI, as defined
    using nonparametric statistics

    - Details: http://www.ucl.ac.uk/ich/short-courses-events/about-stats-courses/stats-rm/Chapter_8_Content/confidence_interval_single_median
    - 1.96 is the factor computed for 0.95 confidence limit
    """
    n = len(s)
    if n >= 10:
        s_median = s.median()
        lo_rank = int(np.rint(n / 2.0 - 1.96 * np.sqrt(n) / 2.0))
        hi_rank = int(np.rint(1 + n / 2.0 + 1.96 * np.sqrt(n) / 2.0))
        s_sorted = sorted(s.values.tolist())
        lo_val = s_sorted[lo_rank]
        hi_val = s_sorted[hi_rank]
        return s_median, lo_val, hi_val, 0
    else:
        # Not enough data to construct CI
        return None, None, None, 1


def ci_reduction(data, sample_size_min=10, sample_size_max=None, max_rep_count=20):
    if not sample_size_max:
        sample_size_max = len(data)

    ci = []
    for sample_size in range(sample_size_min, sample_size_max + 1):

        rep_count = min(max_rep_count, ncr(sample_size_max, sample_size))
        for rep in range(rep_count):

            # Use different seed for each repetition
            np.random.seed()

            selected_sample = data.sample(sample_size)
            med, ci_lb, ci_ub, errc = median_and_ci(selected_sample)

            if not errc:
                ci.append({"rep": rep,
                           "sample_size": sample_size,
                           "med": med,
                           "ci_lb": ci_lb,
                           "ci_ub": ci_ub})

    return pd.DataFrame(ci)


def ci_reduction_trial(input_tuple):
    (data, sample_size_min, sample_size_max, rep) = input_tuple

    # Use different seed for each repetition
    np.random.seed()

    res = []

    # Skip some samples sizes for large sets -- do not consider every sample size to accelerate processing
    if sample_size_max < 200:
        # Every value
        studied_range = range(sample_size_min, sample_size_max + 1)
    elif sample_size_max < 500:
        # Fewer after 200, every second
        studied_range = range(sample_size_min, 200) + range(200, sample_size_max + 1, 2)
    elif sample_size_max < 1000:
        # In addition to previous range, even fewer after 500, every 10
        studied_range = range(sample_size_min, 200) + range(200, 500, 2) + range(500, sample_size_max + 1, 10)
    elif sample_size_max < 2000:
        # In addition to previous range, even fewer after 1000, every 50
        studied_range = range(sample_size_min, 200) + range(200, 500, 2) + range(500, 1000, 10) + range(1000, sample_size_max + 1, 50)
    else:
        # In addition to previous range, even fewer after 1000, every 100
        studied_range = range(sample_size_min, 200) + range(200, 500, 2) + range(500, 1000, 10) + range(1000, 2000, 50) + range(2000, sample_size_max + 1, 100)

    for sample_size in studied_range:

        selected_sample = data.sample(sample_size)
        med, ci_lb, ci_ub, errc = median_and_ci(selected_sample)

        if not errc:
            res.append({"rep": rep,
                       "sample_size": sample_size,
                       "med": med,
                       "ci_lb": ci_lb,
                       "ci_ub": ci_ub})

    return pd.DataFrame(res)


def ci_reduction_parallel(data, sample_size_min=10, sample_size_max=None, max_rep_count=20):
    """ Parallel version of ci_reduction()"""

    if not sample_size_max:
        sample_size_max = len(data)

    if sample_size_max >= sample_size_min:

        tasks = [(data, sample_size_min, sample_size_max, idx) for idx in range(max_rep_count)]

        #p = mp.Pool(mp.cpu_count())
        # Save 2 cores for other tasks
        p_count = max(mp.cpu_count() - 2, 1)
        p = mp.Pool(p_count)

        tasks_output = p.map(ci_reduction_trial, tasks)

        # Important to terminate processes
        p.terminate()

        all_output = pd.concat(tasks_output)
    else:
        all_output = pd.DataFrame()

    return all_output
    

def calculate_reps(df_indiv, allowed_err):
    if len(df_indiv) > 0:
        df_avg = df_indiv.groupby(['sample_size']).mean()
        df_avg["desired_lb"] = df_avg.med - allowed_err * df_avg.med
        df_avg["desired_ub"] = df_avg.med + allowed_err * df_avg.med
        df_avg["stopping_ub"] = df_avg["ci_ub"] <= df_avg["desired_ub"]
        df_avg["stopping_lb"] = df_avg["ci_lb"] >= df_avg["desired_lb"]
        df_avg["stopping"] = df_avg["stopping_lb"] & df_avg["stopping_ub"]
        df_avg["sample_size"] = df_avg.index.values
    else:
        df_avg = pd.DataFrame()

    ci_can_stop = df_avg[df_avg["stopping"] == True]
    if len(ci_can_stop):
        stop_at_sample_size_idx = ci_can_stop.index.min()
        stop_at_sample_size = df_avg.at[stop_at_sample_size_idx, "sample_size"]
    else:
        stop_at_sample_size_idx = None
        stop_at_sample_size = None

    return stop_at_sample_size_idx
