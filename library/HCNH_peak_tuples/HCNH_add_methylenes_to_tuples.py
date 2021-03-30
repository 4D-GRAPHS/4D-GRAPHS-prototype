import numpy as np
import pandas as pd

from library.HCNH_peak_features.HCNH_compute_methylenes.compute_methylenes_common import create_symmetric_methylene_pairs


def HCNH_compute_tuples_with_methylenes(HCNH_selected_tuples_df, HCNH_methylene_pairs_df):
    return _add_methylenes_to_tuples(HCNH_methylene_pairs_df, HCNH_selected_tuples_df) \
        .sort_values(by=['atom']) \
        .sort_values(by=['tuple_index'], kind='merge')


def _add_methylenes_to_tuples(HCNH_methylene_pairs_df, HCNH_peaks_df):
    symmetric_pairs = create_symmetric_methylene_pairs(HCNH_methylene_pairs_df)

    second_meth = HCNH_peaks_df \
        .merge(symmetric_pairs, on='peak_index', how='left') \
        .pipe(lambda df: df.assign(
        meth_peak=df.apply(lambda row: row['peak_index'] if np.isnan(row['meth_peak']) else row['meth_peak'], axis=1))) \
        .astype({'meth_peak': 'int64'}) \
        .drop('peak_index', axis=1) \
        .rename(columns={'meth_peak': 'peak_index'})
    return pd.concat([HCNH_peaks_df, second_meth])