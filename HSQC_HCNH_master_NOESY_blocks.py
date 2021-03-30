import pandas as pd
from EXEC_scripts.EXEC_input_processing import EXEC_HSQC_input_transform, EXEC_HSQC_input_cleanup, \
    EXEC_HCNH_input_transform
from EXEC_scripts.EXEC_HCNH_peak_features import EXEC_HCNH_classify_CA_peaks, EXEC_HCNH_compute_frames, \
    EXEC_HCNH_compute_histogram_predictions, EXEC_HCNH_compute_methylenes, EXEC_HCNH_threshold_histograms, \
    EXEC_HCNH_detect_aromatics
from EXEC_scripts.EXEC_HCNH_common_peaks import EXEC_HCNH_compute_common_peaks, EXEC_HCNH_count_common_peaks, \
    EXEC_HCNH_compute_cpframes, EXEC_HCNH_read_precomputed_intersections

from EXEC_scripts.EXEC_HCNH_acid_prediction.EXEC_HCNH_acid_prediction_tuples_rf import \
    EXEC_HCNH_compute_acid_prediction_ftuples, \
    EXEC_HCNH_compute_acid_prediction_tuples_rf_cpframes

from EXEC_scripts.EXEC_HCNH_acid_prediction.EXEC_HCNH_acid_prediction_doublet_based_rf import \
    EXEC_HCNH_aggregate_tuple_predictions_doublet_subtuples_frames, \
    EXEC_HCNH_compute_1_2_tuples_frames, EXEC_HCNH_compute_acid_prediction_1_2_tuples_rf_frames, \
    EXEC_HCNH_extract_final_predictions_frames, \
    EXEC_HCNH_aggregate_tuple_predictions_doublet_subtuples_cpframes, EXEC_HCNH_extract_final_predictions_cpframes

from EXEC_scripts.EXEC_HCNH_peak_tuples import EXEC_HCNH_add_methylenes_to_cpftuples, EXEC_HCNH_compute_tuples_cpframes, \
    EXEC_HCNH_compute_tuples_frames, \
    EXEC_HCNH_compute_tuples_max_length_frames, \
    EXEC_HCNH_select_cpftuples, EXEC_HCNH_add_methylenes_to_ftuples, EXEC_HCNH_select_ftuples

from commons.fasta_parser import get_protein_sequence_list
from library.input_processing.guess_starting_residue import guess_starting_residue
from commons.flow_control_enums import EdgeWeightType


def EXEC_HCNH_HSQC_input_processing(HSQC_sparky_input_file, FASTA_file, HCNH_sparky_input_file, Settings):
    HSQC_peaks_df = EXEC_HSQC_input_transform(HSQC_sparky_input_file, Settings.generated_file('_HSQC_peaks.csv'))

    protein_sequence_list = get_protein_sequence_list(FASTA_file, Settings.protein)

    STARTING_RESID = guess_starting_residue(HSQC_peaks_df, protein_sequence_list)

    HSQC_spectrum_df = EXEC_HSQC_input_cleanup(HSQC_peaks_df, protein_sequence_list, STARTING_RESID, rtolHN=0.005,
                                               rtolN=0.015, Settings=Settings)

    HCNH_spectrum_df = EXEC_HCNH_input_transform(HCNH_sparky_input_file,
                                                 Settings.generated_file('_HCNH_spectrum.csv'))

    return protein_sequence_list, HSQC_spectrum_df, STARTING_RESID, HCNH_spectrum_df


def EXEC_compute_HCNH_peak_features(HCNH_spectrum_df, HSQC_spectrum_df, Settings):
    HCNH_probCA_df = EXEC_HCNH_classify_CA_peaks(HCNH_spectrum_df, Settings=Settings)
    HCNH_frames_df = EXEC_HCNH_compute_frames(HCNH_spectrum_df, HSQC_spectrum_df, Settings=Settings)
    HCNH_histograms_df = EXEC_HCNH_compute_histogram_predictions(HCNH_spectrum_df, Settings=Settings)
    HCNH_histograms_thresholded_df = EXEC_HCNH_threshold_histograms(HCNH_histograms_df, Settings=Settings)
    HCNH_aromatics_df = EXEC_HCNH_detect_aromatics(HCNH_spectrum_df, Settings=Settings)
    HCNH_methylene_pairs = EXEC_HCNH_compute_methylenes(
        HCNH_frames_df, HCNH_spectrum_df, HCNH_histograms_df, Settings=Settings)

    return HCNH_probCA_df, HCNH_frames_df, HCNH_histograms_df, HCNH_histograms_thresholded_df, \
           HCNH_aromatics_df, HCNH_methylene_pairs


def EXEC_compute_HCNH_connectivities(HCNH_frames_df, HCNH_spectrum_df, Settings):
    HCNH_common_peaks_df = EXEC_HCNH_compute_common_peaks(
        HCNH_frames_df, HCNH_frames_df, HCNH_spectrum_df, Settings=Settings)
    HCNH_cpframes_df = EXEC_HCNH_compute_cpframes(
        HCNH_common_peaks_df, HCNH_frames_df, Settings=Settings)
    HCNH_common_peaks_count_df = EXEC_HCNH_count_common_peaks(HCNH_cpframes_df, Settings=Settings)
    if Settings.what_edge_weight == EdgeWeightType.intersections:
        HCNH_intersections_df = EXEC_HCNH_read_precomputed_intersections(Settings=Settings)
    else:
        HCNH_intersections_df = None

    return HCNH_common_peaks_df, HCNH_cpframes_df, HCNH_common_peaks_count_df, HCNH_intersections_df


def EXEC_compute_HCNH_tuples(HCNH_frames_df, HCNH_cpframes_df, HCNH_histograms_df, HCNH_histograms_thresholded_df,
                             HCNH_spectrum_df, HCNH_methylene_pairs_df, Settings):
    HCNH_ftuples_df = EXEC_HCNH_compute_tuples_frames(
        HCNH_frames_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df, Settings=Settings)
    HCNH_ftuples_selected_df = EXEC_HCNH_select_ftuples(HCNH_ftuples_df, HCNH_histograms_df, Settings=Settings)
    HCNH_ftuples_with_methylenes_df = EXEC_HCNH_add_methylenes_to_ftuples(
        HCNH_ftuples_selected_df, HCNH_methylene_pairs_df, Settings=Settings)

    HCNH_cpftuples_df = EXEC_HCNH_compute_tuples_cpframes(
        HCNH_cpframes_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df, Settings=Settings)
    HCNH_cpftuples_selected_df = EXEC_HCNH_select_cpftuples(HCNH_cpftuples_df, HCNH_histograms_df, Settings=Settings)
    HCNH_cpftuples_with_methylenes_df = EXEC_HCNH_add_methylenes_to_cpftuples(
        HCNH_cpftuples_selected_df, HCNH_methylene_pairs_df, Settings=Settings)

    HCNH_cpftuples_max_len_df = EXEC_HCNH_compute_tuples_max_length_frames(HCNH_cpftuples_df, Settings=Settings)

    return HCNH_ftuples_with_methylenes_df, HCNH_cpftuples_with_methylenes_df, HCNH_cpftuples_max_len_df


def EXEC_compute_HCNH_predictions_tuples_alg(HCNH_ftuples_with_methylenes_df, HCNH_cpftuples_with_methylenes_df,
                                             HCNH_spectrum_df, HCNH_aromatics_df,
                                             Settings):
    HCNH_frames_acid_prediction_df = EXEC_HCNH_compute_acid_prediction_ftuples(
        HCNH_ftuples_with_methylenes_df, HCNH_spectrum_df, HCNH_aromatics_df, Settings=Settings)
    HCNH_cpframes_acid_prediction_df = EXEC_HCNH_compute_acid_prediction_tuples_rf_cpframes(
        HCNH_cpftuples_with_methylenes_df, HCNH_spectrum_df, HCNH_aromatics_df, Settings=Settings)

    return HCNH_frames_acid_prediction_df, HCNH_cpframes_acid_prediction_df


def EXEC_compute_HCNH_predictions_doublet_alg(
        HCNH_frames_df, HCNH_cpframes_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df, HCNH_aromatics_df,
        HCNH_methylene_pairs_df, Settings):
    # POSSIBLE CLASH OF TWO ALGORITHMS (WHEN DOUBLET EXECUTED AFTER MAX_TUPLE

    # COMPUTE 1,2 TUPLES AND PREDICT ACID ON THEM
    HCNH_1_2_tuples_frames_df = EXEC_HCNH_compute_1_2_tuples_frames(
        HCNH_frames_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df, Settings=Settings)

    # HACK!! Computing tpl_tags from tuples with methylenes
    tpl_tags = HCNH_1_2_tuples_frames_df \
        .groupby('tuple_index') \
        .apply(lambda df: tuple(df.drop_duplicates('peak_index').loc[:, 'peak_index'].sort_values())) \
        .rename('tpl_tag')

    # HACK!! Doubling peaks - methylenes are completely ignored!
    HCNH_1_2_tuples_frames_doubling_peaks_methylenes_ignored_df = \
        pd.concat([HCNH_1_2_tuples_frames_df, HCNH_1_2_tuples_frames_df])

    HCNH_1_2_tuples_frames_preds_df = EXEC_HCNH_compute_acid_prediction_1_2_tuples_rf_frames(
        HCNH_1_2_tuples_frames_doubling_peaks_methylenes_ignored_df,
        HCNH_spectrum_df, HCNH_aromatics_df, Settings=Settings) \
        .merge(tpl_tags, left_on='tpl_idx', right_index=True, how='left')

    # PREDICT ACID ON HCNH FRAMES
    frames_aggregated_tuple_predictions_df = EXEC_HCNH_aggregate_tuple_predictions_doublet_subtuples_frames(
        HCNH_frames_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df, HCNH_1_2_tuples_frames_preds_df,
        Settings=Settings)

    frames_final_predictions_df = EXEC_HCNH_extract_final_predictions_frames(
        frames_aggregated_tuple_predictions_df, Settings=Settings)

    # PREDICT ACID ON HCNH CPFRAMES
    cpframes_aggregated_tuple_predictions_df = EXEC_HCNH_aggregate_tuple_predictions_doublet_subtuples_cpframes(
        HCNH_cpframes_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df, HCNH_1_2_tuples_frames_preds_df,
        Settings=Settings)

    cpframes_final_predictions_df = EXEC_HCNH_extract_final_predictions_cpframes(
        cpframes_aggregated_tuple_predictions_df, Settings=Settings)

    return frames_final_predictions_df, cpframes_final_predictions_df
