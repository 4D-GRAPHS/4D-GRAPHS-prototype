from commons.bio_nmr_constants import aatype_maxH_C_pairs_dict
from library.HCNH_common_peaks.HCNH_compute_common_peaks import common_peaks_df_from_cpframes_df


def weights_from_relative_max_tuple_length(HCNH_cpftuples_max_len_df):
    HCNH_cpftuples_max_len_df['weight'] = HCNH_cpftuples_max_len_df.apply(
        lambda x: min(x['max_tuple_len'] / aatype_maxH_C_pairs_dict[x['acid']], 1.0)
        if x['max_tuple_len'] > 1 else 1 / 20,
        axis=1
    )

    return common_peaks_df_from_cpframes_df(HCNH_cpftuples_max_len_df)
