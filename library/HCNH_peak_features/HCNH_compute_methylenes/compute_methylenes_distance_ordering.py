import numpy as np
from sklearn.preprocessing import minmax_scale
import pandas as pd

from commons.bio_nmr_constants import methylenes
from library.join_peak_features_with_peaks import join_common_peaks_with_features, join_peaks_with_features


def _manhattan_distance_with_intensity(peak_pair):
    return abs(peak_pair['source_scaled_C'] - peak_pair['target_scaled_C']) + \
           abs(peak_pair['source_scaled_HC'] - peak_pair['target_scaled_HC']) + \
           abs(peak_pair['source_scaled_intensity'] - peak_pair['target_scaled_intensity'])


# %%

def _compute_methylene_pairs_for_frames(frame_df, C_threshold, histograms_threshold):
    frame_poss_meth_df = frame_df[frame_df["methylene_prob"] >= histograms_threshold]

    frame_poss_meth_df = frame_poss_meth_df \
        .assign(scaled_intensity=minmax_scale(frame_poss_meth_df['intensity'])) \
        .assign(scaled_C=minmax_scale(frame_poss_meth_df['C'])) \
        .assign(scaled_HC=minmax_scale(frame_poss_meth_df['HC']))

    close_peaks = frame_poss_meth_df.apply(
        lambda peak1: frame_poss_meth_df.apply(
            lambda peak2: (abs(peak1.C - peak2.C) <= C_threshold) and (peak1.peak_index < peak2.peak_index), axis=1),
        axis=1)

    if not close_peaks.any(axis=None):
        return pd.DataFrame({'source_peak_index': [], 'target_peak_index': []})

    pairs_with_distance = join_common_peaks_with_features(
        pd.DataFrame({'source_peak_index': list(frame_poss_meth_df['peak_index'].iloc[np.where(close_peaks)[0]]),
                      'target_peak_index': list(frame_poss_meth_df['peak_index'].iloc[np.where(close_peaks)[1]])}),
        frame_poss_meth_df[['peak_index', 'scaled_C', 'scaled_HC', 'scaled_intensity']]) \
                              .pipe(lambda df: df.assign(dist=df.apply(_manhattan_distance_with_intensity, axis=1))) \
                              .loc[:, ['source_peak_index', 'target_peak_index', 'dist']]

    return pd \
               .concat(
        [pairs_with_distance, pairs_with_distance.rename(columns={'source_peak_index': 'target_peak_index',
                                                                  'target_peak_index': 'source_peak_index'})]) \
               .sort_index() \
               .sort_values(by='dist', kind='merge') \
               .drop_duplicates(subset=['source_peak_index'], keep='first') \
               .drop_duplicates(subset=['target_peak_index'], keep='first') \
               .pipe(lambda df: df.loc[df.groupby(df.index).size().apply(lambda x: x > 1)]) \
               .pipe(lambda df: df.groupby(df.index).first()) \
               .loc[:, ['source_peak_index', 'target_peak_index']]


def HCNH_compute_methylenes_distance_ordering(
        HCNH_frames_df, HCNH_spectrum_df, HCNH_histograms_df, C_threshold, histogram_threshold):
    HCNH_methylenes_prob_df = HCNH_histograms_df \
                                  .assign(
        methylene_prob=HCNH_histograms_df.loc[:, ['hist_' + meth_col for meth_col in methylenes]].max(axis=1)) \
                                  .loc[:, ['peak_index', 'methylene_prob']]

    return join_peaks_with_features(HCNH_frames_df, HCNH_spectrum_df, HCNH_methylenes_prob_df) \
        .groupby('frame') \
        .apply(_compute_methylene_pairs_for_frames, C_threshold, histogram_threshold) \
        .rename(columns={'source_peak_index': 'peak1', 'target_peak_index': 'peak2'}) \
        .astype({'peak1': 'int64', 'peak2': 'int64'}) \
        .reset_index(drop=True)
