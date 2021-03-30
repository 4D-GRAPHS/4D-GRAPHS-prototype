from commons.bio_nmr_constants import aatype_max_H_C_pairs_no_methylenes_dict


def _multiply_by_factor(row):
    return row["weight"] * (row["arity"] / aatype_max_H_C_pairs_no_methylenes_dict[row["acid"]]) \
        if row["should_mult_by_factor"] else row["weight"]


def acid_predictions_from_tuples_to_frames(acid_prediction_on_tuples_df):
    acid_prediction_on_tuples_df = acid_prediction_on_tuples_df.reset_index(drop=True)

    return acid_prediction_on_tuples_df \
        .assign(weight=acid_prediction_on_tuples_df.apply(_multiply_by_factor, axis=1)) \
        .pipe(lambda df: df.iloc[df \
              .loc[:, ['frame', 'acid', 'weight']] \
              .groupby(['frame', 'acid']) \
              .idxmax().loc[:, 'weight']])