import bz2
import pickle
from functools import reduce
from itertools import chain

import numpy as np
import pandas as pd

from sklearn.preprocessing import minmax_scale

from library.join_peak_features_with_peaks import join_hnnh_peaks_with_common_peaks_features, join_peaks_with_features


def load_pickle(fname, object_num=1000000):
    """
        Method to load a variable number of objects from a pickled file.
        It returns a list with the objects loaded from the pickle file.
    """
    object_list = []
    with bz2.BZ2File(fname, "rb") as pickled_file:
        unpickler = pickle.Unpickler(pickled_file)
        for i in range(object_num):
            try:
                object_list.append(unpickler.load())
            except EOFError:
                break
    return object_list


def compute_peaknum_intratio(valid_HNNH_connectivities_df, HNNH_connectivities_df, threshold):
    def _assign_value(g):
        return g.assign(**{"peaknum_intratio_ge_%.1f" % threshold:
                               HNNH_connectivities_df.loc[(HNNH_connectivities_df["frame1"] == g.frame1.iloc[0]) &
                                                          (HNNH_connectivities_df["HNNH_intensity_ratio"] >= threshold),
                               :].shape[0]})

    return valid_HNNH_connectivities_df[["frame1"]].groupby("frame1", as_index=False) \
        .apply(lambda g: _assign_value(g)).droplevel(1)


def create_QNsc_featvec(valid_HNNH_connectivities_df,
                        HNNH_connectivities_df,
                        HNNH_frames_with_QNsc_condition_QNsc_prob_df,
                        HCNH_connectivities_occupancy_intersection_df,
                        QNsc_score_rf_file,
                        create_full_QNsc_featvecs=False):
    """
    This function creates the feature vectors that are input to the node_weight_predictor.

    param: valid_HNNH_connectivities_df: contains only HNNH connectivities that satisfy the 1) Name and Resonance
    Condition ("reverse_conn==True"), and the 2) Highest intensity condition (the side-chain should be the
    strongest peak for the given frame).

    Use 'create_full_QNsc_featvecs = True' only for the development of the node weight predictor
    """

    if create_full_QNsc_featvecs:
        feature_names = ["frame1", "frame2", "HNNH_total_num_peaks",
                         "HNNH_intensity_ratio", "occupancy", "relative_occupancy", "intersection",
                         "conditional_distance", "deltaHN", "deltaN", "prob_UNK"] + [
                            "peaknum_intratio_ge_%.1f" % thr
                            for thr in
                            [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4,
                             0.3, 0.2, 0.1]]
    else:
        feature_names = load_pickle(QNsc_score_rf_file, object_num=1)[0]

    intratio_df_list = [compute_peaknum_intratio(valid_HNNH_connectivities_df, HNNH_connectivities_df,
                                                 float(f.replace("peaknum_intratio_ge_", "")))
                        for f in feature_names if f.startswith("peaknum_intratio_ge_")]

    # The source and target frames in HNNH_connectivities_df can be in either of both directions,
    # therefore pd.concat is not the correct approach. Instead iterate over each row of HNNH_connectivities_df
    # and add the respective conditional_distance,prob_ASN,prob_GLN,prob_UNK values.
    QNsc_featvecs_df = HNNH_connectivities_df.merge(HNNH_frames_with_QNsc_condition_QNsc_prob_df \
                                                    .groupby(["frame1", "frame2", "peak_index"], as_index=False) \
                                                    .apply(np.mean), on=["frame1", "frame2", "peak_index"]) \
        .merge(valid_HNNH_connectivities_df, on=["frame1", "frame2", "HNNH_total_num_peaks", "HNNH_num_common_peaks",
                                                 'HNNH_scaled_intensity', 'reverse_conn', 'HNNH_intensity_ratio']) \
        .merge(HCNH_connectivities_occupancy_intersection_df \
               .rename(columns={"source_frame": "frame1", "target_frame": "frame2",
                                "num_common_peaks": "HCNH_num_common_peaks"}),
               on=["frame1", "frame2"]) \
        .sort_values(by="conditional_distance")

    return reduce(lambda df1, df2: pd.merge(df1, df2, on='frame1'),
                  [QNsc_featvecs_df] + intratio_df_list)[["frame1", "frame2"] + feature_names]


def compute_node_scores_on_csv(QNsc_featvecs_csv, out_QNsc_scores_csv):
    QNsc_featvecs_df = pd.read_csv(QNsc_featvecs_csv)
    return predict_QNsc_using_rf(QNsc_featvecs_df, out_QNsc_scores_csv, )


def get_single_frame_QNsc_prob(QNsc_featvecs_df):
    def average_Nsc_prob(row):
        # this works even if the target-source frame pair doesn't exist, but in this case it should in order to
        # satisfy the QNsc condition
        mean_QNsc_prob = np.mean(QNsc_featvecs_df.loc[(QNsc_featvecs_df["frame2"] == row["frame1"]) &
                                                      (QNsc_featvecs_df["frame1"] == row[
                                                          "frame2"]), "QNsc_prob"].tolist() +
                                 [row["QNsc_prob"]])
        return [row["frame1"], mean_QNsc_prob], [row["frame2"], mean_QNsc_prob]

    return average_Nsc_prob


def predict_QNsc_using_rf(QNsc_featvecs_df, HCNH_frames_df, QNsc_score_rf_file):
    # load the node weight predictor along with the optimum probability threshold
    feature_names, rf, best_thr = load_pickle(QNsc_score_rf_file)
    X = QNsc_featvecs_df[feature_names]
    QNsc_featvecs_df["QNsc_prob"] = rf.predict_proba(X)[:, 1].tolist()

    # HNNH contains pairs of frames. We want only one QNsc_prob for each frame (the average)
    df = pd.DataFrame(
        data=list(chain(*QNsc_featvecs_df.apply(get_single_frame_QNsc_prob(QNsc_featvecs_df), axis=1))),
        columns=["frame", "score"])

    # average multiple occurrences of the same frame
    df = pd.DataFrame(data=map(lambda frame:
                               [frame, df.loc[df["frame"] == frame, "score"].mean()],
                               set(df["frame"])),
                      columns=["frame", "score"])

    # set the score of all frames with QNSc_prob (renamed to "score")>=best_thr to 1, and then
    # revert them to become weights and scale them to [0,1].
    df["weight"] = minmax_scale(-1 * df.apply(lambda r: 1.0 if r["score"] >= best_thr else r["score"], axis=1))

    return pd.DataFrame(data=[[frame, df.loc[df["frame"] == frame, "weight"].values[0]]
                              if frame in df["frame"].values else [frame, 1.0]
                              for frame in HCNH_frames_df["frame"].drop_duplicates()],
                        columns=["frame", "weight"]).drop_duplicates()


def HNNH_HCNH_QNsc_prediction(HNNH_frames_df, HNNH_scaled_intensities_df, HNNH_connectivities_df,
                              HNNH_common_peaks_df, HNNH_common_peaks_delta_HN,
                              HNNH_sidechain_probability_df,
                              HCNH_intersection_df, HCNH_frames_df, QNsc_score_rf_file, Settings):
    # Joining HNNH peak features and renaming for compatibility with create_QNsc_featvec.
    # Keep only frames that satisfy both the 1) Name and Resonance Condition ("reverse_conn==True") and the
    # 2) Highest intensity condition (the side-chain should be the strongest peak for the given frame).
    HNNH_connectivities_df = join_peaks_with_features(HNNH_frames_df,
                                                      HNNH_connectivities_df,
                                                      HNNH_scaled_intensities_df) \
        .rename(columns={"num_common_peaks": "HNNH_num_common_peaks",
                         "total_num_peaks": "HNNH_total_num_peaks",
                         "scaled_intensity": "HNNH_scaled_intensity",
                         "intensity_ratio": "HNNH_intensity_ratio"})
    # TODO: alter the selected columns depending on the node_weight_predictor that you have trained.
    valid_HNNH_connectivities_df = \
        HNNH_connectivities_df.loc[(HNNH_connectivities_df["reverse_conn"] == True) &
                                   (HNNH_connectivities_df["HNNH_intensity_ratio"] == 1.0),
                                   ["frame1", "frame2", "HNNH_num_common_peaks", "HNNH_total_num_peaks",
                                    "HNNH_scaled_intensity", "reverse_conn", "HNNH_intensity_ratio"]]

    # Joining HNNH common peaks features and renaming for compatibility with create_QNsc_featvec
    HNNH_frames_with_QNsc_condition_QNsc_prob_df = join_hnnh_peaks_with_common_peaks_features(
        HNNH_frames_df,
        HNNH_common_peaks_df,
        HNNH_common_peaks_delta_HN,
        HNNH_sidechain_probability_df)

    # Computing feature vectors for (yet another) sidechain prediction
    QNsc_featvecs_df = create_QNsc_featvec(valid_HNNH_connectivities_df,
                                           HNNH_connectivities_df,
                                           HNNH_frames_with_QNsc_condition_QNsc_prob_df,
                                           HCNH_intersection_df,
                                           QNsc_score_rf_file,
                                           create_full_QNsc_featvecs=False)

    # Uncomment this line only for the development of the node weight predictor and set above
    # 'create_full_QNsc_featvecs=True'
    # QNsc_featvecs_df.to_csv(Settings.generated_file("_QNsc_featvecs.csv"),
    #                         index=False, sep=",", float_format="%g")

    return predict_QNsc_using_rf(QNsc_featvecs_df, HCNH_frames_df, QNsc_score_rf_file)
