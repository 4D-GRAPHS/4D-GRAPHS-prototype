import logging

from commons.EXEC_caching import EXEC_caching_decorator
from library.compute_weights.node_weights.compute_node_weights_from_QNsc_prediction import weights_from_QNsc_prediction

lg = logging.getLogger(__name__)


@EXEC_caching_decorator(lg, "Computing node weights.", "_node_weight.csv")
def EXEC_compute_node_weights(HNNH_HCNH_QNsc_prediction_df, Settings):
    node_weight_df = weights_from_QNsc_prediction(HNNH_HCNH_QNsc_prediction_df)
    return node_weight_df
