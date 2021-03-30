import os

from commons.flow_control_enums import EdgeAcidWeightType, EdgeWeightType, PredictionAlgType, CommonPeaksAlg, \
    MethylenesAlg, NHPeakDistanceMeasure, NHPeakClosenesMeasure, TupleKind


class Settings:
    protein = '3NIK'

    # General execution control
    number_of_processors = 10
    number_of_processors_for_acid_prediction = 10

    force_computation = True

    compute_node_weights = True
    compute_NHmap = True
    # --

    # General dirs
    NMR_PIPELINE_ROOT = os.path.dirname(os.path.realpath(__file__))
    execution_dir = NMR_PIPELINE_ROOT + "/execution_dir/"
    data_dir = NMR_PIPELINE_ROOT + "/input/"
    precomputed_data_dir = NMR_PIPELINE_ROOT + "/precomputed_data/"
    # --

    # **********

    # HCNH Peak features computation parameters

    # HCNH frames computation parameters
    HCNH_frames_NH_distance_measure_name = NHPeakDistanceMeasure.manhattan
    HCNH_frames_NH_closenes_measure_name = NHPeakClosenesMeasure.absolute_differences_thresholded
    HCNH_frames_N_SCALING_FACTOR = 0.15
    HCNH_frames_N_BOUND = 0.3
    HCNH_frames_H_BOUND = 0.03
    # --

    # HCNH histograms
    HCNH_histograms_threshold = 0.00025
    # --

    # Aromatics
    HCNH_aromatics_Cthreshold = 100
    # --

    # Methylene pairs computation parameters
    HCNH_methylenes_alg = MethylenesAlg.agglomerative_clustering
    HCNH_methylenes_C_threshold = 0.3
    HCNH_methylenes_histogram_threshold = 0.00000001
    # --

    # **********

    # HCNH connectivities computation parameters
    HCNH_common_peaks_CH_closenes_condition_name = 'C_H_absolute_differences_thresholded'
    HCNH_common_peaks_CH_distance_measure_name = 'euclidean'
    HCNH_common_peaks_C_bound = 0.4
    HCNH_common_peaks_H_bound = 0.04

    max_intersection_val = 1
    # --

    # *****

    # HCNH tuples computation parameters

    # HCNH tuples computation
    HCNH_ftuples_kind = TupleKind.max_tuple
    HCNH_ftuples_lengths_list = [None]
    HCNH_cpftuples_kind = TupleKind.max_tuple
    HCNH_cpftuples_lengths_list = [None]
    # --

    # HCNH tuples filtering
    HCNH_ftuples_number_of_selected = 5
    HCNH_ftuples_remove_singlets = False
    HCNH_cpftuples_number_of_selected = 5
    HCNH_cpftuples_remove_singlets = False
    # --

    # HCNH aa prediction on tuples parameters
    HCNH_tuples_alg_ftuples_ignore_arity_one = True
    HCNH_tuples_alg_ftuples_arity_one_default_value = 1 / 20
    HCNH_tuples_alg_cpftuples_ignore_arity_one = True
    HCNH_tuples_alg_cpftuples_arity_one_default_value = 1 / 20
    # --

    # HCNH aa prediction doublet based parameters
    HCNH_doublet_alg_ftuples_kind = TupleKind.n_tuple
    HCNH_doublet_alg_ftuples_lengths_list = [1, 2]
    HCNH_doublet_alg_ftuples_ignore_arity_one = False
    HCNH_doublet_alg_ftuples_arity_one_default_value = 1 / 20  # not used if HCNH_doublet_alg_ftuples_ignore_arity_one = False
    HCNH_doublet_alg_normalize_predictions = False
    # --

    # *****

    # Algorithm options
    #what_edge_weight = EdgeWeightType.intersections
    what_edge_weight = EdgeWeightType.common_peaks_count_0_1
    what_edge_acid_weight = EdgeAcidWeightType.rf_acid_prediction
    common_peaks_alg = CommonPeaksAlg.max_tuple_selection
    what_prediction_alg = PredictionAlgType.tuples_algorithm
    # --

    # *****

    # Learning models dirs
    HCNH_histograms_model_dir = NMR_PIPELINE_ROOT + '/models/histograms/HC_correlated_smoothed_histograms/'
    HCNH_aa_predictor_rf_model_dir = NMR_PIPELINE_ROOT + '/models/rf/rf_models_from_cosh/aa_type_predictors/'
    HCNH_PRO_predictor_rf_model_dir = NMR_PIPELINE_ROOT + '/models/rf/rf_models_from_cosh/PRO_predictors/'
    HCNH_CA_predictor_rf_model = NMR_PIPELINE_ROOT + '/models/rf/CA_rf.pickle'
    HN_asn_gln_prediction_model = NMR_PIPELINE_ROOT + '/models/rf/asn_gln_model_rewritten.pickle'
    QNsc_score_rf = NMR_PIPELINE_ROOT + "/models/QNsc_score_rf/QNsc_scorer_rf.pkl"

    # --

    @staticmethod
    def generated_file(file):
        return Settings.execution_dir + Settings.protein + file

    @staticmethod
    def raw_input_file(file):
        return Settings.data_dir + "/" + Settings.protein + "/" + Settings.protein + file
