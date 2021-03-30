import logging

from EXEC_scripts.EXEC_HCNH_acid_prediction.EXEC_HCNH_acid_prediction_tuples_rf import lg
from commons.EXEC_caching import EXEC_caching_decorator
from library.HCNH_acid_prediction.HCNH_acid_prediction_doublet_based.HCNH_aggregate_tuple_predictions_doublet_subtuples import \
    HCNH_aggregate_tuple_predictions_doublet_subtuples
from library.HCNH_acid_prediction.HCNH_acid_prediction_doublet_based.HCNH_extract_final_predictions import \
    HCNH_extract_final_predictions
from library.HCNH_acid_prediction.HCNH_acid_prediction_max_tuples.HCNH_compute_rf_acid_prediction import \
    HCNH_compute_acid_prediction_on_tuples_df
from library.HCNH_peak_tuples.HCNH_compute_tuples import HCNH_compute_tuples_for_frames_df

lg = logging.getLogger(__name__)


# COMPUTE 1,2 TUPLES AND PREDICT ACID ON THEM

@EXEC_caching_decorator(lg, "Computing 1, 2 tuples for HCNH frames.",
                        '_HCNH_1_2_max_ftuples.csv')
def EXEC_HCNH_compute_1_2_tuples_frames(HCNH_frames_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df, Settings):
    return HCNH_compute_tuples_for_frames_df(
        HCNH_frames_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df,
        Settings.HCNH_doublet_alg_ftuples_kind, Settings.HCNH_doublet_alg_ftuples_lengths_list,
        Settings.number_of_processors)


@EXEC_caching_decorator(lg, "Computing rf acid predictions for HCNH frames on 1, 2 tuples.",
                        '_HCNH_frames_acid_prediction_on_1_2_tuples.csv')
def EXEC_HCNH_compute_acid_prediction_1_2_tuples_rf_frames(
        HCNH_1_2_tuples_frames_df, HCNH_spectrum_df, HCNH_aromatic_df, Settings):
    return HCNH_compute_acid_prediction_on_tuples_df(
        HCNH_1_2_tuples_frames_df, HCNH_spectrum_df, HCNH_aromatic_df,
        Settings.HCNH_aa_predictor_rf_model_dir, Settings.HCNH_PRO_predictor_rf_model_dir,
        ignore_arity_one=Settings.HCNH_doublet_alg_ftuples_ignore_arity_one,
        arity_one_default_value=Settings.HCNH_doublet_alg_ftuples_arity_one_default_value,
        number_of_processors=Settings.number_of_processors)


# PREDICT ACID ON HCNH FRAMES

@EXEC_caching_decorator(lg, "Computing predictions hierarchy of doublet subtuples for frames.",
                        '_frames_preds_hierarchy.csv')
def EXEC_HCNH_aggregate_tuple_predictions_doublet_subtuples_frames(
        HCNH_frames_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df, HCNH_1_2_tuples_frames_preds_df, Settings):
    return HCNH_aggregate_tuple_predictions_doublet_subtuples(
        HCNH_frames_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df, HCNH_1_2_tuples_frames_preds_df)


@EXEC_caching_decorator(lg, "Extracting final predictions from pred hierarchy for frames.",
                        "_frames_acid_prediction.csv")
def EXEC_HCNH_extract_final_predictions_frames(frames_aggregated_tuple_predictions_df, Settings):
    return HCNH_extract_final_predictions(frames_aggregated_tuple_predictions_df,
                                          Settings.HCNH_doublet_alg_normalize_predictions)


# PREDICT ACID ON HCNH CPFRAMES

@EXEC_caching_decorator(lg, "Computing predictions hierarchy of doublet subtuples for cpframes.",
                        '_cpframes_preds_hierarchy.csv')
def EXEC_HCNH_aggregate_tuple_predictions_doublet_subtuples_cpframes(
        HCNH_cpframes_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df, HCNH_frames_1_2_tuples_preds_df, Settings):
    return HCNH_aggregate_tuple_predictions_doublet_subtuples(
        HCNH_cpframes_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df, HCNH_frames_1_2_tuples_preds_df)


@EXEC_caching_decorator(lg, "Extracting final predictions from pred hierarchy for cpframes.",
                        "_common_peaks_acid_prediction.csv")
def EXEC_HCNH_extract_final_predictions_cpframes(cpframes_pred_hierarchy_df, Settings):
    return HCNH_extract_final_predictions(cpframes_pred_hierarchy_df, Settings.HCNH_doublet_alg_normalize_predictions)
