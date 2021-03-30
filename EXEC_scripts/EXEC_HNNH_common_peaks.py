from commons.EXEC_caching import EXEC_caching_decorator
from library.HNNH_common_peaks.HNNH_compute_common_peaks import HNNH_compute_common_peaks_on_df
from library.HNNH_common_peaks.HNNH_compute_common_peaks_QNsc_sidechain_probability import \
    HNNH_compute_common_peaks_QNsc_sidechain_probabilities
from library.HNNH_common_peaks.HNNH_compute_common_peaks_delta_HN import \
    HNNH_compute_common_peak_delta_HN_df

import logging

lg = logging.getLogger(__name__)


@EXEC_caching_decorator(lg, "Computing HNNH common peaks.",
                        "_HNNH_common_peaks.csv")
def EXEC_HNNH_compute_common_peaks(
        HNNH_frames_df, HNNH_spectrum_df, tolHN=0.04, tolN=0.4, Settings=None):
    HNNH_common_peaks_df = HNNH_compute_common_peaks_on_df(
        HNNH_frames_df, HNNH_spectrum_df, tolHN=tolHN, tolN=tolN)
    return HNNH_common_peaks_df


@EXEC_caching_decorator(lg, "Computing HNNH QNsc sidechain probabilities.",
                        "_HNNH_common_peaks_QNsc_sidechain_probs.csv")
def EXEC_HNNH_compute_common_peaks_QNsc_side_chain_probabilities(
        HNNH_common_peaks_df, HNNH_spectrum_df, hnnh_asn_gln_predictor_path, Settings):
    HNNH_sidechain_probability_df = HNNH_compute_common_peaks_QNsc_sidechain_probabilities(
        HNNH_common_peaks_df, HNNH_spectrum_df, hnnh_asn_gln_predictor_path)
    return HNNH_sidechain_probability_df


@EXEC_caching_decorator(lg, "Computing HNNH common peaks delta HN.",
                        "_HNNH_common_peaks_delta_HN.csv")
def EXEC_HNNH_compute_common_peaks_delta_HN(HNNH_common_peaks_df, HNNH_spectrum_df, Settings):
    HNNH_common_peak_tolerances_df = HNNH_compute_common_peak_delta_HN_df(
        HNNH_common_peaks_df, HNNH_spectrum_df)
    return HNNH_common_peak_tolerances_df
