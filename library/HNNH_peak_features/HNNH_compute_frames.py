import pandas as pd
from library.nh_peak_features import _compute_NH_frames_on_df

import logging
lg = logging.getLogger(__name__)

def HNNH_compute_frames(HNNH_spectrum_df, HSQC_spectrum_df, NH_distance_measure, NH_closeness_measure):
    HNNH_spectrum_1_df = HNNH_spectrum_df[['peak_index', 'HN1', 'N1']].rename(columns={'HN1': 'HN', 'N1': 'N'})
    HNNH_spectrum_2_df = HNNH_spectrum_df[['peak_index', 'HN2', 'N2']].rename(columns={'HN2': 'HN', 'N2': 'N'})

    # READ THIS!
    lg.warning('The method compute_frames_on_df used to compute HNNH frames removes all peak that do not have'
               'both frames assigned - i.e. at least one of the NH components of the HNNH peak is too far away'
               '(w.r.t. the NH_closeness_measure) from all HSQC peaks.')

    HNNH_frames1_df = _compute_NH_frames_on_df(HNNH_spectrum_1_df, HSQC_spectrum_df,
                                               NH_distance_measure, NH_closeness_measure)

    HNNH_frames2_df = _compute_NH_frames_on_df(HNNH_spectrum_2_df, HSQC_spectrum_df,
                                               NH_distance_measure, NH_closeness_measure)

    # TODO: add_dash_to_NH:  # convert E45NH-F46NH to E45N-H-F46N-H ?
    return pd.merge(HNNH_frames1_df, HNNH_frames2_df, on="peak_index", suffixes=("1", "2"))
