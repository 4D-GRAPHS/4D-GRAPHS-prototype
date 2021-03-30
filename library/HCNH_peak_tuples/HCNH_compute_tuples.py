import pandas as pd
import numpy as np

from commons.bio_nmr_constants import aa_names_code3
from commons.parallel_processing_tools import apply_function_to_list_of_args_and_concat_resulting_dfs
from commons.tuples_from_boolean_df import get_max_tuples, get_all_tuples_of_given_length
from library.join_peak_features_with_peaks import join_peaks_with_features

from commons.flow_control_enums import TupleKind

import logging

lg = logging.getLogger(__name__)


# %%

def _compute_tuples_for_acid_and_frame(acid, frame_id, frame_df, what_tuples, tuple_length, hist_columns_list):
    lg.debug("Processing : " + acid + ' ' + str(frame_id))
    if what_tuples == TupleKind.max_tuple:
        peak_atom_indices_tuples = get_max_tuples(frame_df[frame_df.columns[4:]])
    elif what_tuples == TupleKind.n_tuple:
        peak_atom_indices_tuples = get_all_tuples_of_given_length(frame_df[frame_df.columns[4:]], tuple_length)
    else:
        lg.error("Unknown tuple type.")
        exit()

    tuples = [
        frame_df[['frame', 'peak_index', 'C', 'HC']].iloc[peak_indices].assign(
            atom=list(pd.Series(hist_columns_list)[atom_indices])).assign(
            acid=acid).assign(
            frame_local_tuple_index=tuple_index).assign(arity=len(peak_indices))
        for tuple_index, (peak_indices, atom_indices) in enumerate(peak_atom_indices_tuples)
    ]

    if tuples:
        return pd.concat(tuples)
    else:
        return pd.DataFrame(columns=['frame', 'peak_index', 'C', 'HC'])


# %%

def _compute_tuples_for_frames_and_acid(frames_df, acid, what_tuples, tuple_length):
    lg.info('Processing : ' + acid)

    hist_columns_list = list(frames_df.columns[4:])
    frames_df = frames_df[frames_df[hist_columns_list].any(axis=1)]

    tuples_list = [
        _compute_tuples_for_acid_and_frame(acid, frame[0], frame[1], what_tuples, tuple_length, hist_columns_list)
        for frame in frames_df.groupby('frame', axis=0)]

    if tuples_list:
        return pd.concat(tuples_list)
    else:
        return pd.DataFrame(columns=['frame', 'peak_index', 'C', 'HC'])


# %%

def get_histogram_columns_for_acid(frames_df, acid):
    acid_columns = frames_df.columns.to_series().str.contains(acid)
    acid_hist_columns = list(frames_df.columns[acid_columns])
    frames_df = frames_df[['peak_index', 'frame', 'C', 'HC'] + acid_hist_columns]
    frames_df.columns = ['peak_index', 'frame', 'C', 'HC'] + [x.split('_')[2] for x in acid_hist_columns]
    return frames_df


def _add_tuple_index_to_tuples(tuples_df):
    return pd.concat([
        df[1].assign(tuple_index=ti) for ti, df in
        enumerate(tuples_df.groupby(['frame', 'acid', 'frame_local_tuple_index', 'arity']))
    ])[['peak_index', 'frame', 'tuple_index', 'acid', 'atom']]


def _compute_tuples_for_frames_and_acids(frames_df, acids, what_tuples, tuple_length):
    lg.info('Processing : ' + str(acids))

    results = [
        _compute_tuples_for_frames_and_acid(get_histogram_columns_for_acid(frames_df, acid), acid,
                                            what_tuples, tuple_length) for acid in acids
    ]

    lg.info('Concatenating results for ' + str(acids))

    return pd.concat(results, axis=0)

    # %%

    # INTERFACE
    # frames_df is expected to contain:
    # frames, thresholded histograms, is_aromatic, HCNH spectrum


# INTERFACE
# frames_df is expected to contain:
# frames, thresholded histograms, is_aromatic, HCNH spectrum
def HCNH_compute_tuples_for_frames_df(frames_df, histograms_thresholded_df, spectrum_df,
                                      what_tuples, tuple_lengths_list,
                                      number_of_processors):
    frames_df = join_peaks_with_features(frames_df, histograms_thresholded_df, spectrum_df)

    args_list = [
        (frames_df, acids, what_tuples, tuple_length)
        for acids in [list(acids_array) for acids_array in np.array_split(aa_names_code3, number_of_processors)]
        for tuple_length in tuple_lengths_list]

    tuples_for_frames_and_acid = apply_function_to_list_of_args_and_concat_resulting_dfs(
        _compute_tuples_for_frames_and_acids, args_list,
        number_of_processors, 0, lg)

    return _add_tuple_index_to_tuples(tuples_for_frames_and_acid)
