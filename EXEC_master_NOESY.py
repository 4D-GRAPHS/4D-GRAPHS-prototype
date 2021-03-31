from EXEC_scripts.EXEC_HNNH_HCNH_predictors import EXEC_HNNH_HCNH_QNsc_prediction
from NOESY_master_settings import Settings
import sys
import getopt
import pretty_errors
import logging
import os
import pandas as pd
from library.join_peak_features_with_peaks import join_peaks_with_features

lg = logging.getLogger(__name__)

# COMMAND LINE PROCESSING - CAN OVERWRITE VARIABLES FROM Settings
try:
    opts, args = getopt.getopt(sys.argv[1:], "hp:f", ["help", "protein=", "force"])
except getopt.GetoptError:
    print(sys.argv[0] + " -p <protein> -f")
    sys.exit(1)
for opt, arg in opts:
    if opt == '-h':
        print(sys.argv[0] + " -p <protein> -f")
        print("  -p <protein> sets protein name")
        print("  -f force re-computation")
        sys.exit(0)
    if opt in ("-p", "--protein"):
        Settings.protein = arg
    if opt in ("-f", "--force"):
        Settings.force_computation = True

if not os.path.exists(Settings.raw_input_file('_HNNH.list')):
    Settings.compute_node_weights = False

import subprocess

from HNNH_master_NOESY_blocks import EXEC_HNNH_input_processing, EXEC_HNNH_peak_features, \
    EXEC_HNNH_common_peaks_features
from commons.logger import logger
from library.evaluate.evaluate_NHmap import evaluate_NHmap
from commons.flow_control_enums import PredictionAlgType

print("Log level: ", logger.level)

from HSQC_HCNH_master_NOESY_blocks import EXEC_compute_HCNH_peak_features, EXEC_compute_HCNH_connectivities, \
    EXEC_compute_HCNH_predictions_tuples_alg, EXEC_HCNH_HSQC_input_processing, EXEC_compute_HCNH_tuples, \
    EXEC_compute_HCNH_predictions_doublet_alg

from EXEC_scripts.EXEC_compute_weights.EXEC_compute_edge_weights import EXEC_compute_edge_weights
from EXEC_scripts.EXEC_compute_weights.EXEC_compute_edge_acid_weights import EXEC_compute_edge_acid_weights
from EXEC_scripts.EXEC_compute_weights.EXEC_compute_node_weights import EXEC_compute_node_weights
from EXEC_scripts.EXEC_compute_weights.EXEC_compute_node_acid_weights import EXEC_compute_node_acid_weights

# INPUT PROCESSING - COMPUTING HSQC and HCNH SPECTRA
protein_sequence_list, HSQC_spectrum_df, STARTING_RESID, HCNH_spectrum_df = \
    EXEC_HCNH_HSQC_input_processing(HSQC_sparky_input_file=Settings.raw_input_file('_HSQC.list'),
                                    FASTA_file=Settings.raw_input_file('.fasta'),
                                    HCNH_sparky_input_file=Settings.raw_input_file('_HCNH.list'),
                                    Settings=Settings)

#  COMPUTING HCNH PEAK FEATURES
HCNH_probCA, HCNH_frames_df, HCNH_histograms_df, HCNH_histograms_thresholded_df, \
HCNH_aromatics_df, HCNH_methylene_pairs_df = \
    EXEC_compute_HCNH_peak_features(HCNH_spectrum_df, HSQC_spectrum_df, Settings=Settings)

# COMPUTING HCNH CONNECTIVES
HCNH_common_peaks_df, HCNH_cpframes_df, HCNH_common_peaks_count_df, HCNH_intersections_df = \
    EXEC_compute_HCNH_connectivities(HCNH_frames_df, HCNH_spectrum_df, Settings=Settings)

# HCNH TUPLES
HCNH_ftuples_with_methylenes_df, HCNH_cpftuples_with_methylenes_df, HCNH_cpftuples_max_len_df = \
    EXEC_compute_HCNH_tuples(HCNH_frames_df, HCNH_cpframes_df, HCNH_histograms_df, HCNH_histograms_thresholded_df,
                             HCNH_spectrum_df, HCNH_methylene_pairs_df,
                             Settings=Settings)

# HNCH FRAMES ACID PREDICTION
if Settings.what_prediction_alg == PredictionAlgType.tuples_algorithm:
    HCNH_frames_acid_prediction_df, HCNH_cpframes_acid_prediction_df = \
        EXEC_compute_HCNH_predictions_tuples_alg(
            HCNH_ftuples_with_methylenes_df, HCNH_cpftuples_with_methylenes_df, HCNH_spectrum_df, HCNH_aromatics_df,
            Settings=Settings)
elif Settings.what_prediction_alg == PredictionAlgType.doublet_based_algorithm:
    HCNH_frames_acid_prediction_df, HCNH_cpframes_acid_prediction_df = \
        EXEC_compute_HCNH_predictions_doublet_alg(
            HCNH_frames_df, HCNH_cpframes_df, HCNH_histograms_thresholded_df, HCNH_spectrum_df,
            HCNH_aromatics_df, HCNH_methylene_pairs_df,
            Settings=Settings)
else:
    raise (Exception("Unknown HCNH prediction algorithm!"))

# HNNH processing
if Settings.compute_node_weights:
    # INPUT PROCESSING - COMPUTING HNNH SPECTRUM
    HNNH_spectrum_df = \
        EXEC_HNNH_input_processing(
            HNNH_sparky_input_file=Settings.raw_input_file('_HNNH.list'), Settings=Settings)

    # COMPUTING HNNH PEAK FEATURES
    HNNH_frames_df, HNNH_scaled_intensities_df, HNNH_mean_resonances_df, HNNH_connectivities_df = \
        EXEC_HNNH_peak_features(HNNH_spectrum_df, HSQC_spectrum_df, Settings=Settings)

    # COMPUTING HNNH COMMON PEAKS (PAIRED HNNH PEAKS) FEATURES
    HNNH_common_peaks_df, HNNH_common_peaks_delta_HN, HNNH_QNsc_sidechain_probability_df = \
        EXEC_HNNH_common_peaks_features(HNNH_frames_df, HNNH_spectrum_df, Settings=Settings)

    HNNH_HCNH_sidechain_prediction_df = EXEC_HNNH_HCNH_QNsc_prediction(
        HNNH_frames_df, HNNH_scaled_intensities_df, HNNH_connectivities_df,
        HNNH_common_peaks_df, HNNH_common_peaks_delta_HN, HNNH_QNsc_sidechain_probability_df,
        HCNH_intersections_df, HCNH_frames_df,
        Settings.QNsc_score_rf,
        Settings=Settings)

# Graph alg inputs
edge_weight_df = EXEC_compute_edge_weights(
    HCNH_common_peaks_count_df, HCNH_intersections_df, Settings=Settings)

edge_acid_weight_df = EXEC_compute_edge_acid_weights(
    HCNH_cpframes_acid_prediction_df, HCNH_cpftuples_max_len_df, Settings=Settings)

if Settings.compute_node_weights:
    node_weight_df = EXEC_compute_node_weights(HNNH_HCNH_sidechain_prediction_df, Settings=Settings)

node_acid_weight_df = EXEC_compute_node_acid_weights(HCNH_frames_acid_prediction_df, Settings=Settings)

# NH-mapping
if Settings.compute_NHmap:

    extra_args = " "
    if Settings.compute_node_weights:
        extra_args += "--node-weight %s" % Settings.generated_file('_node_weight.csv')

    command = "graph_alg/graph-core --seq %s --edge-weight %s --edge-acid-weight %s --node-acid-weight %s " \
              "--paths 1 --out %s %s" % \
              (Settings.raw_input_file('.fasta'),
               Settings.generated_file('_edge_weight.csv'),
               Settings.generated_file("_edge_acid_weight.csv"),
               Settings.generated_file('_node_acid_weight.csv'),
               Settings.generated_file('_NHmap.csv'),
               extra_args)
    lg.info("Launching NH-mapping algorithm:\n%s" % command)
    subprocess.call(command.split())
    #evaluate_NHmap(NHmap_csv=Settings.generated_file('_NHmap.csv'),
    #               protein_sequence_list=protein_sequence_list,
    #               start_resid=STARTING_RESID)

    # Generate output NH mapping
    out_file = 'output_NHmapping.csv'
    NHmap_df = pd.read_csv(Settings.generated_file('_NHmap.csv'))
    NHmap_df['ground_truth_aa'] = NHmap_df['sequence_rank'].apply(lambda index: protein_sequence_list[index])
    join_peaks_with_features(NHmap_df.merge(HCNH_frames_df, on='frame'), HCNH_spectrum_df) \
        .to_csv(out_file, index=None)
    print("Result was stored in " + out_file + ".")
