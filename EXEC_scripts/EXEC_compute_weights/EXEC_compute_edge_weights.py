import logging
from commons.flow_control_enums import EdgeWeightType
from commons.EXEC_caching import EXEC_caching_decorator
from library.compute_weights.edge_weights.edge_weights_from_intersections import weights_from_intersections
from library.compute_weights.edge_weights.edge_weights_from_common_peaks_normalized_0_1 import \
    weights_from_common_peaks_normalized_0_1

lg = logging.getLogger(__name__)


@EXEC_caching_decorator(lg, "Computing edge weights.", '_edge_weight.csv')
def EXEC_compute_edge_weights(HCNH_common_peaks_count_df, HCNH_intersections_df, Settings):
    if Settings.what_edge_weight == EdgeWeightType.intersections:
        edge_weight_df = weights_from_intersections(HCNH_common_peaks_count_df, HCNH_intersections_df,
                                                    Settings.max_intersection_val)
    elif Settings.what_edge_weight == EdgeWeightType.common_peaks_count_0_1:
        edge_weight_df = weights_from_common_peaks_normalized_0_1(HCNH_common_peaks_count_df)
    return edge_weight_df
