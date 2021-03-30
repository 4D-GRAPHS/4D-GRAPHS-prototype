def weights_from_common_peaks_normalized_0_1(HCNH_common_peaks_count_df):
    HCNH_common_peaks_count_df['weight'] = HCNH_common_peaks_count_df['weight'] / (
        max(HCNH_common_peaks_count_df['weight']))
    return HCNH_common_peaks_count_df
