import logging

from commons.EXEC_caching import EXEC_caching_decorator

lg = logging.getLogger(__name__)

from library.HNNH_peak_features.HNNH_compute_connectivities import HNNH_compute_connectivities_on_df
from library.HNNH_peak_features.HNNH_compute_NH_mean_resonances import HNNH_compute_mean_NH_resonances_df
from library.HNNH_peak_features.HNNH_compute_frames import HNNH_compute_frames
from library.peak_distance_measures.NH_peaks_closenes_conditions import NH_absolute_differences_thresholded
from library.peak_distance_measures.NH_peaks_distance_measures import euclidean_peak_distance, manhattan_peak_distance
from library.HNNH_peak_features.HNNH_compute_scaled_intensities import HNNH_compute_scaled_intensities_df


@EXEC_caching_decorator(lg, "Computing HNNH frames.", '_HNNH_frames.csv')
def EXEC_HNNH_compute_frames(
        HNNH_spectrum_df, HSQC_spectrum_df,
        NH_distance_measure_name="euclidean_peak_distance", N_SCALING_FACTOR=1 / 6,
        NH_closenes_measure_name="NH_absolute_differences_thresholded",
        N_BOUND=0.4, H_BOUND=0.04, Settings=None):
    # a function which for two NH peaks returns a distance (a non-negative number)
    NH_distance_measures = {
        "manhattan_peak_distance": manhattan_peak_distance(N_scaling_factor=N_SCALING_FACTOR),
        "euclidean_peak_distance": euclidean_peak_distance(N_scaling_factor=N_SCALING_FACTOR),
    }

    # a boolean function which for two NH peaks indicates whether they are close to each other
    NH_closeness_measures = {
        "NH_absolute_differences_thresholded": NH_absolute_differences_thresholded(N_threshold=N_BOUND,
                                                                                   H_threshold=H_BOUND)
    }

    HNNH_frames_df = HNNH_compute_frames(
        HNNH_spectrum_df, HSQC_spectrum_df,
        NH_distance_measures[NH_distance_measure_name], NH_closeness_measures[NH_closenes_measure_name])

    return HNNH_frames_df


@EXEC_caching_decorator(lg, "Computing mean NH resonances for HNNH peaks.",
                        "_HNNH_mean_resonances.csv")
def EXEC_HNNH_compute_mean_NH_resonances(HNNH_frames_df, HNNH_spectrum_df, Settings):
    HNNH_mean_NH_resonances_df = HNNH_compute_mean_NH_resonances_df(HNNH_frames_df, HNNH_spectrum_df)
    return HNNH_mean_NH_resonances_df


@EXEC_caching_decorator(lg, "Computing scaled intensities of HNNH peaks.",
                        "_HNNH_scaled_intensities.csv")
def EXEC_HNNH_compute_scaled_intensities(HNNH_frames_df, HNNH_spectrum_df, Settings):
    HNNH_scaled_intensities_df = HNNH_compute_scaled_intensities_df(HNNH_frames_df, HNNH_spectrum_df)
    return HNNH_scaled_intensities_df


@EXEC_caching_decorator(lg, "Computing HNNH connectivities.",
                        "_HNNH_connectivities.csv")
def EXEC_HNNH_compute_connectivities(HNNH_frames_df, Settings):
    HNNH_connectivities_df = HNNH_compute_connectivities_on_df(HNNH_frames_df)
    return HNNH_connectivities_df
