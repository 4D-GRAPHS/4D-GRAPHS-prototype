from EXEC_scripts.EXEC_HCNH_acid_prediction.EXEC_HCNH_acid_prediction_tuples_rf import lg
from commons.EXEC_caching import EXEC_caching_decorator
from library.HCNH_peak_tuples.HCNH_add_methylenes_to_tuples import HCNH_compute_tuples_with_methylenes
from library.HCNH_peak_tuples.HCNH_compute_tuples import HCNH_compute_tuples_for_frames_df
from library.HCNH_peak_tuples.HCNH_compute_tuples_max_length import compute_tuples_max_length_df
from library.HCNH_peak_tuples.HCNH_filter_tuples import select_HCNH_tuples

# COMPUTE AND SELECT TUPLES FOR HCNH FRAMES

@EXEC_caching_decorator(lg, "Computing tuples for HCNH frames.", '_HCNH_ftuples.csv')
def EXEC_HCNH_compute_tuples_frames(HCNH_frames_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df, Settings):
    return HCNH_compute_tuples_for_frames_df(
        HCNH_frames_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df,
        Settings.HCNH_ftuples_kind, Settings.HCNH_ftuples_lengths_list,
        Settings.number_of_processors)


@EXEC_caching_decorator(lg, "Selecting tuples for HCNH frames.",
                        '_HCNH_selected_ftuples.csv')
def EXEC_HCNH_select_ftuples(HCNH_ftuples_df, HCNH_histograms_df, Settings):
    return select_HCNH_tuples(
        HCNH_ftuples_df, HCNH_histograms_df,
        Settings.HCNH_ftuples_number_of_selected, Settings.HCNH_ftuples_remove_singlets)


@EXEC_caching_decorator(lg, "Adding methylene pairs to tuples for HCNH frames.",
                        '_HCNH_ftuples_with_methylenes.csv')
def EXEC_HCNH_add_methylenes_to_ftuples(
        HCNH_ftuples_df, methylene_pairs_df, Settings):
    return HCNH_compute_tuples_with_methylenes(HCNH_ftuples_df, methylene_pairs_df)


# COMPUTE AND SELECT TUPLES FOR HCNH CPFRAMES

@EXEC_caching_decorator(lg, "Computing tuples for HCNH cpframes.",
                        '_HCNH_cpftuples.csv')
def EXEC_HCNH_compute_tuples_cpframes(
        HCNH_cpframes_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df, Settings):
    HCNH_cpftuples_df = HCNH_compute_tuples_for_frames_df(
        HCNH_cpframes_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df,
        Settings.HCNH_cpftuples_kind, Settings.HCNH_cpftuples_lengths_list, Settings.number_of_processors)
    return HCNH_cpftuples_df


@EXEC_caching_decorator(lg, "Selecting tuples for HCNH cpframes.",
                        '_HCNH_selected_cpftuples.csv')
def EXEC_HCNH_select_cpftuples(
        HCNH_cpftuples_df, HCNH_histograms_df, Settings):
    return select_HCNH_tuples(
        HCNH_cpftuples_df, HCNH_histograms_df,
        Settings.HCNH_cpftuples_number_of_selected, Settings.HCNH_cpftuples_remove_singlets)


@EXEC_caching_decorator(lg, "Adding methylene pairs to ftuples for HCNH cpframes.",
                        '_HCNH_cpftuples_with_methylenes.csv')
def EXEC_HCNH_add_methylenes_to_cpftuples(
        HCNH_cpftuples_df, methylene_pairs_df, Settings):
    return HCNH_compute_tuples_with_methylenes(HCNH_cpftuples_df, methylene_pairs_df)


# COMPUTE AND SELECT MAX TUPLES FOR HCNH CPFRAMES

@EXEC_caching_decorator(lg, "Computing max tuples for HCNH frames.",
                        '_HCNH_cpftuples_max_length.csv')
def EXEC_HCNH_compute_tuples_max_length_frames(HCNH_tuples_df, Settings):
    return compute_tuples_max_length_df(HCNH_tuples_df)
