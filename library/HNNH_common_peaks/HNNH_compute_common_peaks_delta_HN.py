import numpy as np

from library.join_peak_features_with_peaks import join_hnnh_common_peaks_with_features


def mean_NH_resonance(pair):
    return np.abs(np.mean([pair['HN2_1'] - pair['HN1_1'], pair['HN1_2'] - pair['HN2_2']]))


def mean_N_resonance(pair):
    return np.abs(np.mean([pair['N2_1'] - pair['N1_1'], pair['N1_2'] - pair['N2_2']]))


def HNNH_compute_common_peak_delta_HN_df(HNNH_common_peaks_df, HNNH_spectrum_df):
    sel_merged = join_hnnh_common_peaks_with_features(HNNH_common_peaks_df, HNNH_spectrum_df)

    return sel_merged \
               .assign(deltaHN=sel_merged.apply(mean_NH_resonance, axis=1)) \
               .assign(deltaN=sel_merged.apply(mean_N_resonance, axis=1)) \
               .loc[:, ['peak_index_1', 'peak_index_2', 'deltaHN', 'deltaN']]
