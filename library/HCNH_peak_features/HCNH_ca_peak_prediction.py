import pickle
import pandas as pd


def HCNH_compute_CA_peak_prob_to_spectrum_df(HCNH_spectrum_df, HCNH_CA_predictor_rf_model):
    PredCA = pickle.load(open(HCNH_CA_predictor_rf_model, "rb"))
    df = HCNH_spectrum_df \
             .loc[:, ['C', 'HC']] \
        .rename({'C': "Creson", 'HC': "HCreson"})

    return pd.DataFrame({
        'peak_index': HCNH_spectrum_df['peak_index'],
        'CA_prob': pd.DataFrame(PredCA.predict_proba(df), columns=PredCA.classes_)[True]
    })


"""
TODO: parameters to be considered in the future for filtering connectivities without common CA peaks.
OFFSET=0.4999, min_peak_num=1
    :param OFFSET: determines the borders of the probability twilight zone, within which zone the fidelity of
                    the CA-HA classifier is questionable (we cannot be sure aboutthe prediction).
    :param min_peak_num: remove only connectivities between AAIGs that have at least 'min_peak_num' matching peaks
                            the most. The lower the more connectivities it removes?
"""
