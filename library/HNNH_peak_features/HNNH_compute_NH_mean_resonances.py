import pandas as pd

from library.join_peak_features_with_peaks import join_peaks_with_features


def HNNH_compute_mean_NH_resonances_df(HNNH_frames_df, HNNH_spectrum_df):
    """
    TODO: the input DataFrame must have columns: HN1, N1, HN2, N2, frame1, frame2.

    Loads the HNNH file with labels copied from HSQC, computes average resonances for the sidechain Classifier.
    STEPS:
    * average and save the N and HN resonances for each residue into new columns
    """

    # Average and save the HN1, N1, HN2, N2 resonances for each residue into new columns
    HNNH_frames_spectrum_df = join_peaks_with_features(HNNH_frames_df, HNNH_spectrum_df)

    mean_resonances_df = pd.concat([
        HNNH_frames_spectrum_df[["frame1", "N1", "HN1"]].rename(columns={"frame1": "frame", "N1": "N", "HN1": "HN"}),
        HNNH_frames_spectrum_df[["frame2", "N2", "HN2"]].rename(columns={"frame2": "frame", "N2": "N", "HN2": "HN"})]) \
        .groupby("frame") \
        .mean(numeric_only=True)

    return HNNH_frames_spectrum_df.merge(mean_resonances_df[["HN", "N"]], left_on="frame1", right_on="frame") \
        .merge(mean_resonances_df, left_on="frame2", right_on="frame") \
        .rename(columns={"N_x": "mean_N1", "HN_x": "mean_HN1", "N_y": "mean_N2", "HN_y": "mean_HN2"})[
        ["peak_index", "mean_HN1", "mean_N1", "mean_N2", "mean_HN2"]
    ]
