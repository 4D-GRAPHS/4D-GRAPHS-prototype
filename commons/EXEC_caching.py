import os

import pandas as pd


def EXEC_caching_decorator(lg, log_text, cache_csv_suffix, **outter_kwargs):
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            lg.info(log_text)
            if 'Settings' not in kwargs:
                raise(Exception("'Settings' must be the keyword argument of every EXEC box!"))

            Settings = kwargs['Settings']

            if 'force_computation' in outter_kwargs.keys():
                fc = outter_kwargs['force_computation']
            else:
                fc = Settings.force_computation

            csv_file = Settings.generated_file(cache_csv_suffix)

            if os.path.exists(csv_file) and (not fc):
                lg.warning("Reading the resulting dataframe from " + cache_csv_suffix)
                return pd.read_csv(csv_file)
            else:
                res = f(*args, **kwargs)
                res.to_csv(csv_file, index=False, sep=",", float_format='%g')
                return res

        return wrapped_f

    return wrap
