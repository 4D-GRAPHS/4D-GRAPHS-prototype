import logging

lg = logging.getLogger(__name__)


def compute_tuples_max_length_df(HCNH_tuples_df):
    tuple_lengths_df = HCNH_tuples_df[["frame", "acid", "tuple_index", "peak_index"]].groupby(
        ["frame", "acid", "tuple_index"]).count()
    max_tuple_length_df = tuple_lengths_df.groupby(['frame', 'acid']).max().reset_index().rename(
        {'peak_index': 'max_tuple_len'}, axis=1)
    return max_tuple_length_df
