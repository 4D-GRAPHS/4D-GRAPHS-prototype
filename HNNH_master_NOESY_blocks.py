from EXEC_scripts.EXEC_input_processing import EXEC_HNNH_input_transform
from EXEC_scripts.EXEC_HNNH_peak_features import EXEC_HNNH_compute_scaled_intensities, EXEC_HNNH_compute_connectivities, \
    EXEC_HNNH_compute_frames, EXEC_HNNH_compute_mean_NH_resonances
from EXEC_scripts.EXEC_HNNH_common_peaks import EXEC_HNNH_compute_common_peaks_delta_HN, EXEC_HNNH_compute_common_peaks, \
    EXEC_HNNH_compute_common_peaks_QNsc_side_chain_probabilities

import logging

lg = logging.getLogger(__name__)


def EXEC_HNNH_input_processing(HNNH_sparky_input_file, Settings):
    HNNH_spectrum_df = EXEC_HNNH_input_transform(HNNH_sparky_input_file=HNNH_sparky_input_file,
                                                 HNNH_peaks_output_csv=Settings.generated_file('_HNNH_spectrum.csv'))

    return HNNH_spectrum_df


def EXEC_HNNH_peak_features(HNNH_spectrum_df, HSQC_spectrum_df, Settings):
    HNNH_frames_df = EXEC_HNNH_compute_frames(
        HNNH_spectrum_df=HNNH_spectrum_df, HSQC_spectrum_df=HSQC_spectrum_df,
        NH_distance_measure_name="euclidean_peak_distance", N_SCALING_FACTOR=1 / 6,
        NH_closenes_measure_name="NH_absolute_differences_thresholded",
        N_BOUND=0.4, H_BOUND=0.04,
        Settings=Settings)

    HNNH_scaled_intensities_df = EXEC_HNNH_compute_scaled_intensities(HNNH_frames_df, HNNH_spectrum_df,
                                                                      Settings=Settings)

    HNNH_mean_resonances_df = EXEC_HNNH_compute_mean_NH_resonances(HNNH_frames_df, HNNH_spectrum_df,
                                                                   Settings=Settings)

    HNNH_connectivities_df = EXEC_HNNH_compute_connectivities(HNNH_frames_df, Settings=Settings)

    return HNNH_frames_df, HNNH_scaled_intensities_df, HNNH_mean_resonances_df, HNNH_connectivities_df


def EXEC_HNNH_common_peaks_features(HNNH_frames_df, HNNH_spectrum_df, Settings):
    HNNH_common_peaks_df = EXEC_HNNH_compute_common_peaks(HNNH_frames_df, HNNH_spectrum_df, tolHN=0.04, tolN=0.4,
                                                          Settings=Settings)

    HNNH_common_peaks_delta_HN = EXEC_HNNH_compute_common_peaks_delta_HN(HNNH_common_peaks_df, HNNH_spectrum_df,
                                                                         Settings=Settings)

    HNNH_common_peaks_QNsc_sidechain_probability_df = \
        EXEC_HNNH_compute_common_peaks_QNsc_side_chain_probabilities(
            HNNH_common_peaks_df, HNNH_spectrum_df,
            Settings.HN_asn_gln_prediction_model,
            Settings=Settings)

    return HNNH_common_peaks_df, HNNH_common_peaks_delta_HN, HNNH_common_peaks_QNsc_sidechain_probability_df
