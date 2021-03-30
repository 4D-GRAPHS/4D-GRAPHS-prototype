import logging

from commons.EXEC_caching import EXEC_caching_decorator
from library.HCNH_peak_features.HCNH_compute_methylenes.compute_methylenes_agglomerative_clustering import \
    HCNH_compute_methylenes_agglomerative_clustering
from library.HCNH_peak_features.HCNH_compute_methylenes.compute_methylenes_distance_ordering import \
    HCNH_compute_methylenes_distance_ordering
from library.HCNH_peak_features.HCNH_compute_methylenes.compute_methylenes_interface import HCNH_compute_methylenes

lg = logging.getLogger(__name__)

from library.HCNH_peak_features.HCNH_ca_peak_prediction import HCNH_compute_CA_peak_prob_to_spectrum_df
from library.nh_peak_features import compute_NH_frames_on_df
from library.HCNH_peak_features.HCNH_threshold_histograms import HCNH_threshold_histograms
from library.HCNH_peak_features.HCNH_identify_aromatics import HCNH_find_aromatics
from library.HCNH_peak_features.HCNH_compute_histogram_predictions import HCNH_compute_histogram_predictions


@EXEC_caching_decorator(lg, "Adding probability of a peak being CA.", '_HCNH_probCA.csv')
def EXEC_HCNH_classify_CA_peaks(HCNH_spectrum_df, Settings):
    return HCNH_compute_CA_peak_prob_to_spectrum_df(HCNH_spectrum_df, Settings.HCNH_CA_predictor_rf_model)


@EXEC_caching_decorator(lg, "Computing HCNH frames.", '_HCNH_frames.csv')
def EXEC_HCNH_compute_frames(HCNH_spectrum_df, HSQC_spectrum_df, Settings):
    return compute_NH_frames_on_df(
        HCNH_spectrum_df, HSQC_spectrum_df,
        Settings.HCNH_frames_N_SCALING_FACTOR, Settings.HCNH_frames_N_BOUND, Settings.HCNH_frames_H_BOUND,
        Settings.HCNH_frames_NH_distance_measure_name, Settings.HCNH_frames_NH_closenes_measure_name)


@EXEC_caching_decorator(lg, "Computing histogram predictions on the HCNH spectrum.",
                        '_HCNH_histograms.csv')
def EXEC_HCNH_compute_histogram_predictions(HCNH_spectrum_df, Settings):
    return HCNH_compute_histogram_predictions(
        HCNH_spectrum_df, Settings.HCNH_histograms_model_dir, Settings.number_of_processors)


@EXEC_caching_decorator(lg, "Thresholding histogram values.", '_HCNH_histograms_thresholded.csv')
def EXEC_HCNH_threshold_histograms(HCNH_histograms_df, Settings):
    return HCNH_threshold_histograms(HCNH_histograms_df, Settings.HCNH_histograms_threshold)


@EXEC_caching_decorator(lg, "Identifying aromatics.", '_HCNH_aromatics.csv')
def EXEC_HCNH_detect_aromatics(HCNH_spectrum_df, Settings):
    return HCNH_find_aromatics(HCNH_spectrum_df, Settings.HCNH_aromatics_Cthreshold)


@EXEC_caching_decorator(lg, "Computing methylene pairs using agglomerative clustering.", '_HCNH_methylene_pairs.csv')
def EXEC_HCNH_compute_methylenes(
        HCNH_frames_df, HCNH_spectrum_df, HCNH_histograms_df, Settings):
    return HCNH_compute_methylenes(
        HCNH_frames_df, HCNH_spectrum_df, HCNH_histograms_df,
        Settings.HCNH_methylenes_C_threshold, Settings.HCNH_methylenes_histogram_threshold,
        Settings.HCNH_methylenes_alg)