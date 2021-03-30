from commons.bio_nmr_constants import aa_names_code3
from library.join_peak_features_with_peaks import join_peaks_with_features


def _get_hist_cols(frames_hist_df, acid):
    acid_columns = frames_hist_df.columns.to_series().str.contains(acid)
    return list(frames_hist_df.columns[acid_columns])


def _select_hist_passing_rows(df, aa_type):
    return (df[_get_hist_cols(df, aa_type)]).any(axis=1)


from commons.bio_nmr_constants import aatype_max_H_C_pairs_no_methylenes_dict
from commons.tuples_from_boolean_df import get_all_tuples_of_given_length


def compute_acid_frame_to_hist_passing_peak_idxs_df(HCNH_frames, HCNH_histograms_thresholded, HCNH_spectrum):
    thresholded_hist_df = join_peaks_with_features(HCNH_frames, HCNH_histograms_thresholded, HCNH_spectrum)

    return {aa_type: {frame_id: {arity: [tuple(frame["peak_index"].iloc[peak_indices].sort_values())
                                         for (peak_indices, _) in
                                         get_all_tuples_of_given_length(frame[_get_hist_cols(frame, aa_type)], arity)]
                                 for arity in range(1, aatype_max_H_C_pairs_no_methylenes_dict[aa_type] + 1)}
                      for frame_id, frame in thresholded_hist_df.groupby("frame")}
            for aa_type in aa_names_code3}
