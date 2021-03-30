from concurrent.futures import ProcessPoolExecutor
import pandas as pd


def execute_function_in_parallel(func, number_of_processors, args_list, lg):
    pool = ProcessPoolExecutor(number_of_processors)

    futures = [
        pool.submit(func, *args)
        for args in args_list
    ]

    results = [
        f.result() for f in futures
    ]

    lg.info("All processes finished!")

    return results


def execute_function_sequentially(func, args_list, lg):
    lg.info("Sequential computation.")

    return [
        func(*args) for args in args_list
    ]


def apply_function_to_list_of_args_and_concat_resulting_dfs(func, df_list, number_of_processors, concat_axis, lg):
    if number_of_processors is None or number_of_processors > 1:
        res = execute_function_in_parallel(func, number_of_processors, df_list, lg)
        lg.info('Concatentaing results of parallel processes.')
        return pd.concat(res, axis=concat_axis)
    else:
        res = execute_function_sequentially(func, df_list, lg)
        return pd.concat(res, axis=concat_axis)
