import pandas as pd
import numpy as np
import functools

from commons.bio_nmr_constants import aa_names_code3
from commons.parallel_processing_tools import apply_function_to_list_of_args_and_concat_resulting_dfs

import logging

lg = logging.getLogger(__name__)


# %%

def _compute_histogram_prediction_on_acid_atom_peak(acid, atom, histogram_probs_per_acid_atom, hist_limits_df, peak):
    H = peak.HC
    C = peak.C
    l = hist_limits_df.loc[(acid, atom)]

    H_min, H_max, C_min, C_max, H_step, C_step, H_row_length = \
        l[['H_min', 'H_max', 'C_min', 'C_max', 'H_step', 'C_step', 'H_row_length']]

    if (H > H_max or H < H_min or
            C > C_max or C < C_min):
        return 0.0

    x = int((H - H_min) / H_step)
    y = int((C - C_min) / C_step)

    index = int(x * H_row_length + y)

    return histogram_probs_per_acid_atom[(acid, atom)].iloc[index]


def _compute_histogram_predictions_on_df_and_acids(HCNH_peaks_df, acids, hist_probs_df, hist_limits_df,
                                                   hist_acid_atom_names):
    lg.info("Processing : " + str(acids))

    histogram_probs_per_acid_atom_dict = {x[0]: x[1]['prob'] for x in
                                          hist_probs_df.reset_index().groupby(['acid', 'atoms'])}

    return pd.DataFrame({
        'hist' + '_' + acid + '_' + atom:
            HCNH_peaks_df.apply(
                functools.partial(_compute_histogram_prediction_on_acid_atom_peak, acid, atom,
                                  histogram_probs_per_acid_atom_dict, hist_limits_df), axis=1
            )
        for acid in acids for atom in hist_acid_atom_names[acid]
    })


# %%

# INTERFACE

def HCNH_compute_histogram_predictions(HCNH_spectrum_df, histograms_model_folder, number_of_processors):
    lg.info("Number of processors : " + str(number_of_processors))
    hist_probs_df = pd.read_csv(histograms_model_folder + "/histograms_vertical_probs.csv",
                                index_col=['acid', 'atoms'])
    hist_limits_df = pd.read_csv(histograms_model_folder + "/histograms_vertical_limit.csv",
                                 index_col=['acid', 'atoms'])
    hist_acid_atom_names = {acid: hist_probs_df.loc[acid].index.unique().to_list() for acid in
                            hist_probs_df.index.get_level_values(0).unique()}

    args_list = [(HCNH_spectrum_df, acid, hist_probs_df,
                  hist_limits_df, hist_acid_atom_names) for acid in
                 [list(acids_array) for acids_array in np.array_split(aa_names_code3, number_of_processors)]]

    HCNH_histograms_df = apply_function_to_list_of_args_and_concat_resulting_dfs(
        _compute_histogram_predictions_on_df_and_acids, args_list, number_of_processors, 1, lg)

    HCNH_histograms_df['peak_index'] = HCNH_spectrum_df['peak_index']

    return HCNH_histograms_df
