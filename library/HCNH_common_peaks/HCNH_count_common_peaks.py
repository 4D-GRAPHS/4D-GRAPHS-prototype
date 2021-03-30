from library.HCNH_common_peaks.HCNH_compute_common_peaks import common_peaks_df_from_cpframes_df


def HCNH_count_common_peaks(common_peaks_df):
    return common_peaks_df_from_cpframes_df(
        common_peaks_df.groupby(['frame']).size().to_frame().reset_index().rename({0: 'weight'}, axis=1))
