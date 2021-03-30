import logging

from commons.EXEC_caching import EXEC_caching_decorator
from library.compute_weights.node_acid_weights.node_acid_weights_from_rf_acid_prediction import \
    weights_from_rf_acid_prediction

lg = logging.getLogger(__name__)


@EXEC_caching_decorator(lg, "Computing node-acid weights.", '_node_acid_weight.csv')
def EXEC_compute_node_acid_weights(HCNH_frames_acid_prediction_df, Settings):
    node_acid_weight_df = weights_from_rf_acid_prediction(HCNH_frames_acid_prediction_df)
    return node_acid_weight_df
