from functools import partial

import pandas as pd
import numpy as np

from commons.signature_processing_utils import lg
from library.peak_distance_measures.CH_peaks_closenes_conditions import get_closenes_condition
from commons.tuples_from_boolean_df import get_max_tuples
from commons.parallel_processing_tools import apply_function_to_list_of_args_and_concat_resulting_dfs
from library.join_peak_features_with_peaks import join_peaks_with_features

from commons.flow_control_enums import CommonPeaksAlg
import logging

from library.join_peak_features_with_peaks import join_common_peaks_with_features
from library.peak_distance_measures.CH_peaks_distance_measures import get_distance_measure

lg = logging.getLogger(__name__)


def _compute_common_peaks_on_source_target_frames_distance_ordered_tuples(source_frame, target_frame,
                                                                          closenes_condition_name_and_args,
                                                                          distance_measure_name_and_args):
    closenes_condition = get_closenes_condition(closenes_condition_name_and_args)
    distance_measure = get_distance_measure(distance_measure_name_and_args,
                                            C_names=['C_1', 'C_2'], H_names=['HC_1', 'HC_2'])

    source_fr = source_frame[1].copy()
    target_fr = target_frame[1].copy()

    connection_matrix = source_fr.apply(
        lambda source_peak: (target_fr.apply(partial(closenes_condition, source_peak), axis=1)), axis=1)

    connection_matrix_true_elements = np.where(connection_matrix)

    if len(connection_matrix_true_elements[0]) == 0:
        return pd.DataFrame(columns=['source_peak_index', 'target_peak_index', 'source_frame', 'target_frame'])

    common_peaks_unsorted = pd.DataFrame({
        'source_peak_index': list(source_frame[1].iloc[connection_matrix_true_elements[0]]['peak_index']),
        'target_peak_index': list(target_frame[1].iloc[connection_matrix_true_elements[1]]['peak_index'])}) \
        .merge(source_fr, left_on='source_peak_index', right_on='peak_index') \
        .merge(target_fr, left_on='target_peak_index', right_on='peak_index', suffixes=['_1', '_2'])

    return common_peaks_unsorted \
               .assign(dist=common_peaks_unsorted \
                       .apply(lambda peak_pair: distance_measure(peak_pair.loc[['C_1', 'HC_1']],
                                                                 peak_pair.loc[['C_2', 'HC_2']]), axis=1)) \
               .sort_values('dist', ascending=True) \
               .drop_duplicates(subset='source_peak_index') \
               .drop_duplicates(subset='target_peak_index') \
               .rename(columns={'frame_1': 'source_frame', 'frame_2': 'target_frame'}) \
               .loc[:, ['source_peak_index', 'target_peak_index', 'source_frame', 'target_frame']]


def _compute_common_peaks_on_source_target_frames_max_tuple_selection(source_frame, target_frame,
                                                                      closenes_condition_name_and_args):
    lg.debug(source_frame[0] + ' -> ' + target_frame[0])

    closenes_condition = get_closenes_condition(closenes_condition_name_and_args)

    connection_matrix = source_frame[1].apply(
        lambda source_peak: (target_frame[1].apply(partial(closenes_condition, source_peak), axis=1)), axis=1)

    max_tuples = get_max_tuples(connection_matrix)

    if max_tuples:
        return pd.DataFrame({
            'source_peak_index': list(source_frame[1].iloc[max_tuples[0][0]]['peak_index']),
            'target_peak_index': list(target_frame[1].iloc[max_tuples[0][1]]['peak_index'])}) \
            .assign(source_frame=source_frame[0]) \
            .assign(target_frame=target_frame[0])
    else:
        return pd.DataFrame(columns=['source_peak_index', 'target_peak_index', 'source_frame', 'targe_frame'])


# %%

def _compute_common_peaks_on_source_target_frames(source_frame, target_frame,
                                                  closenes_condition_name_and_args, distance_measure_name_and_args,
                                                  common_peaks_alg):
    if common_peaks_alg == CommonPeaksAlg.max_tuple_selection:
        return _compute_common_peaks_on_source_target_frames_max_tuple_selection(source_frame, target_frame,
                                                                                 closenes_condition_name_and_args)
    elif common_peaks_alg == CommonPeaksAlg.distance_ordered_tuples:
        return _compute_common_peaks_on_source_target_frames_distance_ordered_tuples(source_frame, target_frame,
                                                                                     closenes_condition_name_and_args,
                                                                                     distance_measure_name_and_args)
    else:
        raise (Exception("Unknown algorithm for common peaks computation."))


# %%

def _compute_common_peaks_on_source_target_df(processor_number, source_frames_df, target_frames_df,
                                              closenes_condition_name_and_args, distance_measure_name_and_args,
                                              common_peaks_alg):
    lg.info("Processor number " + str(processor_number) + " computes common peaks.")

    result = pd.concat([
        _compute_common_peaks_on_source_target_frames(source_frame, target_frame,
                                                      closenes_condition_name_and_args, distance_measure_name_and_args,
                                                      common_peaks_alg)
        for source_frame in source_frames_df.groupby(by='frame')
        for target_frame in target_frames_df.groupby(by='frame')
        if source_frame[0] != target_frame[0]
    ]).loc[:, ['source_frame', 'target_frame', 'source_peak_index', 'target_peak_index']]

    lg.info("Processor number " + str(processor_number) + " finished.")

    return result


# %%

def _HCNH_compute_common_peaks_on_df(source_frames_df, target_frames_df, spectrum_df, closenes_condition_name_and_args,
                                     distance_measure_name_and_args, common_peaks_alg, number_of_processors):
    source_frames_df = join_peaks_with_features(source_frames_df, spectrum_df)
    target_frames_df = join_peaks_with_features(target_frames_df, spectrum_df)

    if number_of_processors > 1:

        source_frames_names_df = pd.DataFrame({'frame': source_frames_df['frame'].unique()})
        number_of_source_frames_for_one_process = source_frames_names_df.shape[0] // (number_of_processors - 1)
        number_of_source_frames_for_last_process = source_frames_names_df.shape[0] % (number_of_processors - 1)

        source_frames_names_df['proc_number'] = [i for i in range(number_of_processors - 1) for k in
                                                 range(number_of_source_frames_for_one_process)] + \
                                                ([number_of_processors - 1] * number_of_source_frames_for_last_process)
        source_frames_df = source_frames_df.merge(source_frames_names_df, on='frame', how='left')

        args_list = [
            (processor_number, source_frame, target_frames_df.copy(), closenes_condition_name_and_args,
             distance_measure_name_and_args, common_peaks_alg) for
            processor_number, source_frame in source_frames_df.groupby('proc_number')
        ]
    else:
        args_list = [
            (0, source_frames_df, target_frames_df, closenes_condition_name_and_args, distance_measure_name_and_args,
             common_peaks_alg)
        ]

    return apply_function_to_list_of_args_and_concat_resulting_dfs(_compute_common_peaks_on_source_target_df, args_list,
                                                                   number_of_processors, 0, lg)


# INTERFACE

def HCNH_compute_common_peaks_on_df(source_frames_df, target_frames_df, spectrum_df,
                                    common_peaks_alg,
                                    CH_closenes_condition_name, C_bound, H_bound, CH_distance_measure_name,
                                    number_of_processors):
    lg.info("Number of processors : " + str(number_of_processors))

    closenes_condition_name_and_args = pd.Series(
        {'name': CH_closenes_condition_name, 'C_bound': C_bound, 'H_bound': H_bound})

    distance_measure_name_and_args = pd.Series(
        {'name': CH_distance_measure_name})

    HCNH_common_peaks_df = _HCNH_compute_common_peaks_on_df(
        source_frames_df, target_frames_df, spectrum_df,
        closenes_condition_name_and_args, distance_measure_name_and_args,
        common_peaks_alg, number_of_processors)

    HCNH_common_peaks_df['peak_index'] = HCNH_common_peaks_df['source_peak_index']
    HCNH_common_peaks_df.drop(['source_frame', 'target_frame'], axis=1, inplace=True)

    return HCNH_common_peaks_df


def HCNH_cpframes_df_from_common_peaks(common_peaks_df, frames_df):
    common_peaks_frames_df = join_common_peaks_with_features(common_peaks_df, frames_df)

    lg.info("Computing cp frames.")

    return pd.DataFrame(
        {'frame': common_peaks_frames_df.source_frame.str.cat(common_peaks_frames_df.target_frame, sep='__'),
         'peak_index': common_peaks_frames_df['peak_index']}
    )


def common_peaks_df_from_cpframes_df(frames_df):
    # inverse to common_peaks_df_to_cpframes_df
    df = frames_df['frame'].str.split("__", n=1, expand=True)
    df.columns = ['source_frame', 'target_frame']
    frames_df = frames_df.drop(['frame'], axis=1)
    return pd.concat([frames_df, df], axis=1)
