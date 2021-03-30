import logging

from commons.EXEC_caching import EXEC_caching_decorator

lg = logging.getLogger(__name__)

from library.HCNH_acid_prediction.HCNH_acid_prediction_max_tuples.HCNH_compute_rf_acid_prediction import \
    HCNH_compute_acid_prediction_on_frames


@EXEC_caching_decorator(lg, "Computing rf acid predictions for HCNH frames.", '_HCNH_frames_acid_prediction.csv')
def EXEC_HCNH_compute_acid_prediction_ftuples(
        HCNH_frames_tuples_with_methylenes_df, HCNH_spectrum_df, HCNH_aromatics_df, Settings):
    return HCNH_compute_acid_prediction_on_frames(
        HCNH_frames_tuples_with_methylenes_df, HCNH_spectrum_df, HCNH_aromatics_df,
        Settings.HCNH_aa_predictor_rf_model_dir, Settings.HCNH_PRO_predictor_rf_model_dir,
        ignore_arity_one=Settings.HCNH_tuples_alg_ftuples_ignore_arity_one,
        arity_one_default_value=Settings.HCNH_tuples_alg_ftuples_arity_one_default_value,
        number_of_processors=Settings.number_of_processors_for_acid_prediction)

@EXEC_caching_decorator(lg, "Computing rf acid predictions for HCNH cpframes.",
                        '_HCNH_cpframes_acid_prediction.csv')
def EXEC_HCNH_compute_acid_prediction_tuples_rf_cpframes(
        HCNH_frames_tuples_with_methylenes_df, HCNH_spectrum_df, HCNH_aromatics_df, Settings):
    return HCNH_compute_acid_prediction_on_frames(
        HCNH_frames_tuples_with_methylenes_df, HCNH_spectrum_df, HCNH_aromatics_df,
        Settings.HCNH_aa_predictor_rf_model_dir, Settings.HCNH_PRO_predictor_rf_model_dir,
        ignore_arity_one=Settings.HCNH_tuples_alg_cpftuples_ignore_arity_one,
        arity_one_default_value=Settings.HCNH_tuples_alg_cpftuples_arity_one_default_value,
        number_of_processors=Settings.number_of_processors_for_acid_prediction)