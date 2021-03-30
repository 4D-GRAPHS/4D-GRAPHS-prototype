import logging

from commons.EXEC_caching import EXEC_caching_decorator
from library.HNNH_HCNH_sidechain_prediction.compute_node_weights_using_rf_DEV import \
    HNNH_HCNH_QNsc_prediction

lg = logging.getLogger(__name__)


@EXEC_caching_decorator(lg, "Computing node weights.", "_node_weight.csv")
def EXEC_HNNH_HCNH_QNsc_prediction(HNNH_frames_df, HNNH_scaled_intensities_df, HNNH_connectivities_df,
                                   HNNH_common_peaks_df, HNNH_common_peaks_delta_HN, HNNH_sidechain_probability_df,
                                   HCNH_intersection_df, HCNH_frames_df, QNsc_score_rf_file, Settings):
    QNsc_prediction_df = HNNH_HCNH_QNsc_prediction(
        HNNH_frames_df, HNNH_scaled_intensities_df, HNNH_connectivities_df,
        HNNH_common_peaks_df, HNNH_common_peaks_delta_HN, HNNH_sidechain_probability_df,
        HCNH_intersection_df, HCNH_frames_df, QNsc_score_rf_file, Settings)
    return QNsc_prediction_df
