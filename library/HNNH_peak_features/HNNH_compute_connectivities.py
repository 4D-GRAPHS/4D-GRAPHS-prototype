from library.join_peak_features_with_peaks import join_peaks_with_features


def form_1direction_HNNH_connectivities_df(HNNH_frames_df):
    """
    Saves only the connectivities that exist in the spectrum without forming the ones in the opposite direction, if they
    don't exit. total_peaknum is frameA-frame*.
    """

    res_df = HNNH_frames_df[["peak_index", "frame1", "frame2"]] \
        .merge(HNNH_frames_df[["frame1", "frame2"]]
               .groupby(["frame1"]).count().rename(columns={"frame2": "total_num_peaks"}), on="frame1") \
        .assign(num_common_peaks=[1] * HNNH_frames_df.shape[0])

    return res_df[["peak_index", "total_num_peaks", "num_common_peaks"]]


def compute_reverse_connectivity_column(HNNH_frame_df):
    """
    Add an extra column to indicate whether both frame1-frame2 and frame2-frame1 connectivities exist.
    """
    res_df = HNNH_frame_df[["peak_index", "frame1", "frame2"]].merge(
        HNNH_frame_df[["frame1", "frame2"]]
            .drop_duplicates()
            .rename(columns={"frame1": "frame2", "frame2": "frame1"})
            .assign(reverse_conn=True), how='left', on=["frame1", "frame2"]) \
        .fillna(False)

    return res_df[["peak_index", "reverse_conn"]]


def HNNH_compute_connectivities_on_df(HNNH_frames_df):
    return join_peaks_with_features(
        form_1direction_HNNH_connectivities_df(HNNH_frames_df),
        compute_reverse_connectivity_column(HNNH_frames_df))
