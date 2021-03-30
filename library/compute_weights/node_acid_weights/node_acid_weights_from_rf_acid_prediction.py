def weights_from_rf_acid_prediction(HCNH_frames_acid_prediction_df):
    return HCNH_frames_acid_prediction_df.loc[:, ['frame', 'acid', 'weight']]
