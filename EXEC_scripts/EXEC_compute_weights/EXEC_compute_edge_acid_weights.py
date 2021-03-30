import logging
from commons.flow_control_enums import EdgeAcidWeightType
from commons.EXEC_caching import EXEC_caching_decorator

from library.compute_weights.edge_acid_weights.edge_acid_weights_from_rf_acid_predictions import \
    weights_from_rf_acid_predictions
from library.compute_weights.edge_acid_weights.edge_acid_weights_from_relative_max_tuple_length import \
    weights_from_relative_max_tuple_length

lg = logging.getLogger(__name__)


@EXEC_caching_decorator(lg, "Computing edge-acid weights.", '_edge_acid_weight.csv')
def EXEC_compute_edge_acid_weights(HCNH_cpframes_acid_prediction_df, HCNH_cpftuples_max_len_df, Settings):
    if Settings.what_edge_acid_weight == EdgeAcidWeightType.relative_max_tuple_length:
        edge_acid_weight_df = weights_from_relative_max_tuple_length(HCNH_cpftuples_max_len_df)
    elif Settings.what_edge_acid_weight == EdgeAcidWeightType.rf_acid_prediction:
        edge_acid_weight_df = weights_from_rf_acid_predictions(HCNH_cpframes_acid_prediction_df)
    return edge_acid_weight_df
