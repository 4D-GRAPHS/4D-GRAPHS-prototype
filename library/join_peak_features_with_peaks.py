import logging

lg = logging.getLogger(__name__)

from functools import reduce
import pandas as pd


def join_peaks_with_features(*peak_features_dfs):
    lg.info("Joining features of peaks.")
    joint_df = reduce(lambda df1, df2: pd.merge(df1, df2, on='peak_index'), peak_features_dfs)
    return joint_df


def join_common_peaks_with_features(common_peaks, *peak_features_dfs):
    lg.info("Joining common peaks with features.")
    return reduce(lambda df1, df2:
                  df1.join(df2.add_prefix('source_').set_index('source_peak_index'),
                           on='source_peak_index').join(
                      df2.add_prefix('target_').set_index('target_peak_index'),
                      on='target_peak_index'),
                  [common_peaks] + list(peak_features_dfs))


def join_hnnh_common_peaks_with_features(hnnh_common_peaks, *peak_features_dfs):
    lg.info("Joining hnnh common peaks with features.")

    joint_1_df = reduce(
        lambda df1, df2: df1.merge(df2.set_index('peak_index'), left_on='peak_index_1', right_index=True),
        [hnnh_common_peaks] + list(peak_features_dfs))

    joint_2_df = reduce(
        lambda df1, df2: df1.merge(df2.set_index('peak_index'), left_on='peak_index_2', right_index=True,
                                   suffixes=['_1', '_2']),
        [joint_1_df] + list(peak_features_dfs))

    return joint_2_df


def join_hnnh_peaks_with_common_peaks_features(hnnh_peaks_df, *hnnh_common_peaks_features):
    lg.info("Joining hnnh common peaks features and hnnh peaks.")
    joint_common_peaks_feature_df = reduce(lambda df1, df2: pd.merge(df1, df2, on=['peak_index_1', 'peak_index_2']),
                                           hnnh_common_peaks_features)

    peak_index_1_features_df = joint_common_peaks_feature_df \
                                   .rename(columns={'peak_index_1': 'peak_index', 'peak_index_2': 'paired_peak_index'}) \
                                   .loc[:,
                               ['peak_index', 'paired_peak_index'] + list(joint_common_peaks_feature_df.columns[2:])]
    peak_index_2_features_df = joint_common_peaks_feature_df \
                                   .rename(columns={'peak_index_2': 'peak_index', 'peak_index_1': 'paired_peak_index'}) \
                                   .loc[:,
                               ['peak_index', 'paired_peak_index'] + list(joint_common_peaks_feature_df.columns[2:])]

    return pd.concat([peak_index_1_features_df, peak_index_2_features_df]).merge(hnnh_peaks_df, on='peak_index')
