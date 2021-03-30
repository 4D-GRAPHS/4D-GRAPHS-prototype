from sklearn.cluster import AgglomerativeClustering
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import manhattan_distances
from sklearn.preprocessing import minmax_scale

from commons.bio_nmr_constants import methylenes
from library.join_peak_features_with_peaks import join_peaks_with_features


def _progressive_clustering_by_CHI(frame_df):
    frame_df = frame_df \
        .assign(scaled_HC=minmax_scale(frame_df["HC"])) \
        .assign(scaled_C=minmax_scale(frame_df["C"])) \
        .sort_values(by="scaled_intensity", ascending=False) \
        .reset_index(drop=True)

    distmat = manhattan_distances(frame_df[["scaled_HC", "scaled_C", "scaled_intensity"]])

    dist_mask = ~np.eye(distmat.shape[0], dtype=bool)

    for local_Cgroup in range(frame_df.shape[0] // 2):
        i, j = np.where(distmat == distmat[dist_mask].min())
        frame_df.loc[i, "local_Cgroup"] = local_Cgroup
        dist_mask[i, :] = False
        dist_mask[:, j] = False

    return frame_df.fillna({'local_Cgroup': frame_df.shape[0] // 2})


def group_frame_carbons(frame_df, C_threshold, histogram_threshold):
    frame_df["scaled_intensity"] = minmax_scale(frame_df["intensity"])
    poss_methylene_df = frame_df[frame_df["methylene_prob"] >= histogram_threshold]

    if poss_methylene_df.shape[0] >= 2:
        Creson_list = poss_methylene_df["C"].values.reshape(-1, 1)
        poss_methylene_df["Cgroup"] = AgglomerativeClustering(distance_threshold=C_threshold,
                                                              n_clusters=None,
                                                              affinity='manhattan',
                                                              linkage='complete') \
            .fit_predict(X=Creson_list)

        poss_methylene_df = poss_methylene_df.groupby("Cgroup", as_index=True) \
            .apply(_progressive_clustering_by_CHI)

    else:
        poss_methylene_df["Cgroup"] = 0

    return poss_methylene_df.reset_index(drop=True)


def group_spectrum_carbons(HCNH_frames_df, HCNH_spectrum_df, HCNH_histograms_df, C_threshold, histogram_threshold):
    HCNH_methylenes_prob_df = HCNH_histograms_df \
                                  .assign(
        methylene_prob=HCNH_histograms_df.loc[:, ['hist_' + meth_col for meth_col in methylenes]].max(axis=1)) \
                                  .loc[:, ['peak_index', 'methylene_prob']]

    HCNH_df = join_peaks_with_features(HCNH_frames_df, HCNH_spectrum_df, HCNH_methylenes_prob_df)

    methylene_groups = HCNH_df \
                           .groupby("frame", as_index=False) \
                           .apply(
        lambda f: group_frame_carbons(f, C_threshold=C_threshold, histogram_threshold=histogram_threshold)) \
                           .reset_index(drop=True) \
                           .loc[:, ['peak_index', 'frame', 'Cgroup', 'local_Cgroup']]

    return pd.concat(
        [e[1][1].assign(methylene_index=e[0]) for e in
         enumerate(methylene_groups.groupby(['frame', 'Cgroup', 'local_Cgroup']))]) \
               .loc[:, ['peak_index', 'methylene_index']]


def HCNH_compute_methylenes_agglomerative_clustering(HCNH_frames_df, HCNH_spectrum_df, HCNH_histograms_df,
                                                     C_threshold, histogram_threshold):
    groups = group_spectrum_carbons(HCNH_frames_df, HCNH_spectrum_df, HCNH_histograms_df,
                                    C_threshold=C_threshold, histogram_threshold=histogram_threshold)

    def _get_methylene_pair(df):
        if df.shape[0] < 2:
            return None
        else:
            p1 = df.iloc[0][0]
            p2 = df.iloc[1][0]

            if p1 > p2:
                p2, p1 = p1, p2
            return pd.DataFrame({'peak1': [p1], 'peak2': [p2]})

    return groups \
        .groupby('methylene_index') \
        .apply(_get_methylene_pair) \
        .reset_index(drop=True) \
        .sort_values('peak1')
