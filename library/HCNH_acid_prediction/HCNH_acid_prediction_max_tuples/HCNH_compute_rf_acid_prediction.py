import numpy as np
import pandas as pd

from commons.bio_nmr_constants import aa_names_code3
from commons.parallel_processing_tools import apply_function_to_list_of_args_and_concat_resulting_dfs
from library.HCNH_acid_prediction.HCNH_acid_prediction_max_tuples.postprocess_acid_predictions_on_tuples import \
    acid_predictions_from_tuples_to_frames
from library.join_peak_features_with_peaks import join_peaks_with_features

import pickle

import logging

lg = logging.getLogger(__name__)


# %%

def _get_horizontal_atom(atom):
    proton1, proton2 = atom['HC']
    mean_carbon = atom['C'].mean()
    if proton1 >= proton2:
        return np.array([mean_carbon, proton1, proton2])
    else:
        return np.array([mean_carbon, proton2, proton1])


# %%

def _get_model_input(tuple_df, acid):
    carbon_inputs = tuple_df \
        .groupby('atom') \
        .apply(_get_horizontal_atom) \
        .sort_values(key=lambda triples: triples \
                     .apply(lambda triple: triple[0]), ascending=False) \
        .pipe(lambda series: np.concatenate(series))

    if acid != 'PRO':
        nitrogen_inputs = np.array([tuple_df.iloc[0]['N'], tuple_df.iloc[0]['HN']])
        input = np.concatenate([carbon_inputs, nitrogen_inputs]).reshape(1, -1)
    else:
        input = carbon_inputs.reshape(1, -1)

    return input


def _eval_model(acid, arity, tuple_df, model, max_acid_arity, ignore_arity_one, arity_one_default_value):
    lg.debug("********************************************************\n" +
             'ACID: ' + acid + ', ARITY: ' + str(arity) + 'true ARITY: ' + str(tuple_df.shape[0]) +
             'MAX acid arity: ' + str(max_acid_arity) + 'TUPLE: ' + str(tuple_df))

    if ignore_arity_one:
        if arity == 1:
            if acid != "GLY":
                return arity_one_default_value, arity, False

    if tuple_df['is_aromatic'].any():
        if acid in ['PHE', 'TYR']:
            arity = arity - (tuple_df['is_aromatic'].sum() / 2)
            tuple_df = tuple_df[tuple_df['is_aromatic'].apply(lambda x: not x)]
            if tuple_df.shape[0] == 0:
                return 1.0, arity, False
        else:
            return 0.0, arity, False

    lg.debug('After removing aromatics: ' + 'arity: ' + str(arity) + ' Tuple: ' + str(tuple_df))

    input = _get_model_input(tuple_df, acid)

    if arity > max_acid_arity:
        lg.warning("WARNING - ARITY LARGER THAN THE MAXIMUM ARITY!!!!!")
        return 0.0, arity, False

    pred = model[acid][arity].predict_proba(input)

    return pred[0][1], arity, True


def _get_tuples_arities_dict(tuples_df):
    return tuples_df \
        .groupby('tuple_index') \
        .apply(lambda tup: tup.atom.drop_duplicates().count())


def _evaluate_model_on_tuples_and_acid(tuples_df, acids, model, ignore_arity_one, arity_one_default_value):
    lg.info('Processing : ' + str(acids))

    tuples_arities_df = _get_tuples_arities_dict(tuples_df)

    result = pd.DataFrame(
        [
            [frame_name,
             tpl_idx,
             acid,
             weight,
             arity,
             should_mult_by_factor
             ]
            for acid in acids
            for (frame_name, tpl_idx), tuple_df in
            tuples_df[tuples_df['acid'] == acid].groupby(['frame', 'tuple_index'], axis=0)
            for weight, arity, should_mult_by_factor in
            [_eval_model(acid, tuples_arities_df.at[tpl_idx], tuple_df,
                         model, max_acid_arity=list(model[acid].keys())[-1],
                         ignore_arity_one=ignore_arity_one, arity_one_default_value=arity_one_default_value)]
        ], columns=['frame', 'tpl_idx', 'acid', 'weight', 'arity', 'should_mult_by_factor'])

    lg.info('Finished : ' + str(acids))

    return result


# %%

# INTERFACE
# frames_df is expected to contain:
# frames, thresholded histograms, is_aromatic, HCNH spectrum
def HCNH_compute_acid_prediction_on_tuples_df(HCNH_tuples_with_methylenes_df, spectrum_df, aromatics_df,
                                              aa_rf_predictor_folder, PRO_rf_predictor_folder,
                                              ignore_arity_one, arity_one_default_value,
                                              number_of_processors):
    lg.info("Number of processors : " + str(number_of_processors))
    lg.warning("If arity is equal to 1, then the probability is " + str(arity_one_default_value) + " for every acid.")

    tuples_df = join_peaks_with_features(HCNH_tuples_with_methylenes_df, spectrum_df, aromatics_df)

    args_list = [(tuples_df[tuples_df['acid'].isin(acids)], acids,
                  {**{acid: pickle.load(
                      open(aa_rf_predictor_folder + "/" + acid + ".pickle", "rb")) for acid
                      in
                      acids if acid != 'PRO'}, **{'PRO': pickle.load(
                      open(PRO_rf_predictor_folder + 'PRO.pickle', 'rb'))}},
                  ignore_arity_one,
                  arity_one_default_value)
                 for acids in
                 [list(acids_array) for acids_array in np.array_split(aa_names_code3, number_of_processors)]]

    return apply_function_to_list_of_args_and_concat_resulting_dfs(_evaluate_model_on_tuples_and_acid, args_list,
                                                                   number_of_processors, 0, lg)


def HCNH_compute_acid_prediction_on_frames(HCNH_tuples_with_methylenes_df, spectrum_df, aromatics_df,
                                           aa_rf_predictor_folder, PRO_rf_predictor_folder,
                                           ignore_arity_one, arity_one_default_value,
                                           number_of_processors):
    HCNH_frames_acid_prediction_df = HCNH_compute_acid_prediction_on_tuples_df(
        HCNH_tuples_with_methylenes_df, spectrum_df, aromatics_df,
        aa_rf_predictor_folder, PRO_rf_predictor_folder,
        ignore_arity_one, arity_one_default_value,
        number_of_processors)
    return acid_predictions_from_tuples_to_frames(HCNH_frames_acid_prediction_df)
