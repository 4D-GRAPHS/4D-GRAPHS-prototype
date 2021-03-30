import pandas as pd

from library.join_peak_features_with_peaks import join_peaks_with_features


def compute_scaled_intensities(HNNH_spectrum_df):
    """
    Scales all intensities in the DataFrame with respect to the maximum intensity of the HNNH spectrum.
    Save the scaled intensities into a new column named "scaled_intensity".
    :return:
    """

    scaled_intensity = HNNH_spectrum_df['intensity'].div(HNNH_spectrum_df['intensity'].max())

    return pd.DataFrame({'peak_index': HNNH_spectrum_df['peak_index'],
                         'scaled_intensity': scaled_intensity})


def compute_frame1_intensity_ratio(HNNH_frames_df, HNNH_scaled_intensity_df):
    """
    Add as an extra column the ratio between the scaled intensity of the given peak wrt the maximum scaled
    intensity of all the peaks with the same frame1.
    """
    HNNH_frames_scaled_intensity_df = join_peaks_with_features(HNNH_frames_df, HNNH_scaled_intensity_df)

    intensity_ratio = HNNH_frames_scaled_intensity_df \
        .merge(HNNH_frames_scaled_intensity_df \
               .groupby("frame1") \
               .apply(lambda f: max(f['scaled_intensity'])) \
               .rename("max_intensity_per_frame1"), on="frame1", how="left") \
        .apply(lambda x: x['scaled_intensity'] / x['max_intensity_per_frame1'], axis=1)

    return pd.DataFrame({'peak_index': HNNH_frames_scaled_intensity_df['peak_index'],
                         'intensity_ratio': intensity_ratio})


def HNNH_compute_scaled_intensities_df(HNNH_frames_df, HNNH_spectrum_df):
    HNNH_scaled_intensity_df = compute_scaled_intensities(HNNH_spectrum_df)
    HNNH_intensity_ratio_df = compute_frame1_intensity_ratio(HNNH_frames_df, HNNH_scaled_intensity_df)
    return join_peaks_with_features(HNNH_scaled_intensity_df, HNNH_intensity_ratio_df)
