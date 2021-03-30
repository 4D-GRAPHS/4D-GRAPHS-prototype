import logging

from commons.EXEC_caching import EXEC_caching_decorator
from library.HCNH_common_peaks.HCNH_read_precomputed_intersections import HCNH_read_precomputed_intersections

lg = logging.getLogger(__name__)

from library.HCNH_common_peaks.HCNH_compute_common_peaks import HCNH_compute_common_peaks_on_df, \
    HCNH_cpframes_df_from_common_peaks
from library.HCNH_common_peaks.HCNH_count_common_peaks import HCNH_count_common_peaks


@EXEC_caching_decorator(lg, "Computing common peaks.", '_HCNH_common_peaks.csv')
def EXEC_HCNH_compute_common_peaks(source_frames_df, target_frames_df, spectrum_df, Settings):
    return HCNH_compute_common_peaks_on_df(
        source_frames_df, target_frames_df, spectrum_df,
        Settings.common_peaks_alg,
        Settings.HCNH_common_peaks_CH_closenes_condition_name,
        Settings.HCNH_common_peaks_C_bound, Settings.HCNH_common_peaks_H_bound,
        Settings.HCNH_common_peaks_CH_distance_measure_name,
        Settings.number_of_processors)


@EXEC_caching_decorator(lg, "Computing cpframes.", '_HCNH_cpframes.csv')
def EXEC_HCNH_compute_cpframes(HCNH_common_peaks_df, HCNH_frames_df, Settings):
    return HCNH_cpframes_df_from_common_peaks(HCNH_common_peaks_df, HCNH_frames_df)


@EXEC_caching_decorator(lg, "Counting the common peaks.", '_common_peaks_count.csv')
def EXEC_HCNH_count_common_peaks(common_peaks_df, Settings):
    return HCNH_count_common_peaks(common_peaks_df)


@EXEC_caching_decorator(lg, "Reading precomputed 2D-histogram intersections.", ('_intersections.csv'))
def EXEC_HCNH_read_precomputed_intersections(Settings):
    return HCNH_read_precomputed_intersections(Settings.precomputed_data_dir, Settings.protein)
