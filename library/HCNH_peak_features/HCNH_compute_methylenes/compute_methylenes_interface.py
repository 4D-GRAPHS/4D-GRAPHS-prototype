from commons.flow_control_enums import MethylenesAlg
from library.HCNH_peak_features.HCNH_compute_methylenes.compute_methylenes_agglomerative_clustering import \
    HCNH_compute_methylenes_agglomerative_clustering
from library.HCNH_peak_features.HCNH_compute_methylenes.compute_methylenes_distance_ordering import \
    HCNH_compute_methylenes_distance_ordering


def HCNH_compute_methylenes(HCNH_frames_df, HCNH_spectrum_df, HCNH_histograms_df,
                            C_threshold, histogram_threshold, compute_methylenes_alg):
    if compute_methylenes_alg == MethylenesAlg.agglomerative_clustering:
        return HCNH_compute_methylenes_agglomerative_clustering(
            HCNH_frames_df, HCNH_spectrum_df, HCNH_histograms_df, C_threshold, histogram_threshold)
    elif compute_methylenes_alg == MethylenesAlg.distance_ordering:
        return HCNH_compute_methylenes_distance_ordering(
            HCNH_frames_df, HCNH_spectrum_df, HCNH_histograms_df, C_threshold, histogram_threshold)
    else:
        raise Exception("Unknown algoritm for computing methylenes.")
