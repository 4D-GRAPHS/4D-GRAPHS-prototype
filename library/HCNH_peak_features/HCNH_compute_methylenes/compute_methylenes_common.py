import pandas as pd


def create_symmetric_methylene_pairs(HCNH_methylene_pairs_df):
    symmetric_pairs = pd.concat([HCNH_methylene_pairs_df,
                                 HCNH_methylene_pairs_df.rename(columns={'peak1': 'peak2', 'peak2': 'peak1'})]) \
        .rename(columns={'peak1': 'peak_index', 'peak2': 'meth_peak'})
    return symmetric_pairs