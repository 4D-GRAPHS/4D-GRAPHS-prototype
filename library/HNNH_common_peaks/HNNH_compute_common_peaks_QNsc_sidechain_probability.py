import pickle

import numpy as np
import pandas as pd

from library.join_peak_features_with_peaks import join_hnnh_common_peaks_with_features


def HNNH_compute_common_peaks_QNsc_sidechain_probabilities(HNNH_common_peaks_df, HNNH_spectrum_df,
                                                           hnnh_asn_gln_predictor_path):
    sel_merged = join_hnnh_common_peaks_with_features(HNNH_common_peaks_df, HNNH_spectrum_df)

    sel_merged_averaged = sel_merged \
                              .assign(
        i_H=sel_merged.apply(lambda peak_pair: np.mean([peak_pair['HN1_1'], peak_pair['HN2_2']]), axis=1)) \
                              .assign(
        j_H=sel_merged.apply(lambda peak_pair: np.mean([peak_pair['HN1_2'], peak_pair['HN2_1']]), axis=1)) \
                              .assign(N=sel_merged.apply(
        lambda peak_pair: np.mean([peak_pair['N1_1'], peak_pair['N2_1'], peak_pair['N1_2'], peak_pair['N2_2']]),
        axis=1)) \
                              .loc[:, ['N', 'i_H', 'j_H']] \
        .rename(columns={'i_H': 'H1', 'j_H': 'H2'})

    # Load pre-trained Random Forest models
    #NMR_PIPELINE_ROOT + '/models/rf/asn_gln_model_multiclass_tested.pickle'
    with open(hnnh_asn_gln_predictor_path,
              'rb') as infile:  # NEW CLASSIFIER
        rf = pickle.load(infile)

    pred = pd.DataFrame(rf.predict_proba(sel_merged_averaged), columns=rf.classes_)\
        .rename(columns={'ASN': 'prob_ASN', 'GLN': 'prob_GLN', 'UNK': 'prob_UNK'})

    return pd.concat([sel_merged, pred], axis=1)[['peak_index_1', 'peak_index_2', 'prob_ASN', 'prob_GLN', 'prob_UNK']] \
        .round({'prob_ASN': 3, 'prob_GLN': 3, 'prob_UNK': 3})
