from library.HCNH_common_peaks.HCNH_compute_common_peaks import common_peaks_df_from_cpframes_df


def weights_from_rf_acid_predictions(HCNH_cpframes_acid_prediction_df):
    return common_peaks_df_from_cpframes_df(HCNH_cpframes_acid_prediction_df.loc[:, ['frame', 'acid', 'weight']])
