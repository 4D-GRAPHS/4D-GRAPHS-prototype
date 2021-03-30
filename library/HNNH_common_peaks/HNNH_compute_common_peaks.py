import math


def HNNH_pair_compute_NH_distance(pair):
    return math.sqrt(
        (pair['HN1_1'] - pair['HN2_2']) ** 2 + \
        ((pair['N1_1'] - pair['N2_2']) / 6) ** 2 + \
        ((pair['N2_1'] - pair['N1_2']) / 6) ** 2 + \
        (pair['HN2_1'] - pair['HN1_2']) ** 2)


def approx_equal_new(x, y, tolerance=0.001):
    return abs(x - y) <= tolerance


def get_is_approx_equal_NH_pair(tolHN, tolN):
    def is_approx_equal_HNNH_pair(pair):
        return approx_equal_new(pair['HN1_1'], pair['HN2_2'], tolHN) and \
               approx_equal_new(pair['N1_1'], pair['N2_2'], tolN) and \
               approx_equal_new(pair['N2_1'], pair['N1_2'], tolN) and \
               approx_equal_new(pair['HN2_1'], pair['HN1_2'], tolHN)

    return is_approx_equal_HNNH_pair


def get_is_max_intensity_HNNH_frame(HNNH_peaks_df):
    def is_max_intensity_HNNH_frame(HNNH_peak):
        frame1, frame2 = HNNH_peak['frame1'], HNNH_peak['frame2']
        frame1_max = HNNH_peaks_df.loc[
            HNNH_peaks_df[lambda p: (p['frame1'] == frame1) | (p['frame2'] == frame1)]['intensity'].idxmax()]
        frame2_max = HNNH_peaks_df.loc[
            HNNH_peaks_df[lambda p: (p['frame1'] == frame2) | (p['frame2'] == frame2)]['intensity'].idxmax()]

        return ((
                        ((frame1_max['frame1'] == frame1) and (frame1_max['frame2'] == frame2)) or
                        ((frame1_max['frame1'] == frame2) and (frame1_max['frame2'] == frame1))
                ) and
                (
                        ((frame2_max['frame1'] == frame1) and (frame2_max['frame2'] == frame2)) or
                        ((frame2_max['frame1'] == frame2) and (frame2_max['frame2'] == frame1))
                ))

    return is_max_intensity_HNNH_frame


from library.join_peak_features_with_peaks import join_peaks_with_features


def HNNH_compute_common_peaks_on_df(HNNH_frames_df, HNNH_spectrum_df, tolHN=0.04, tolN=0.4):
    HNNH_frames_spectrum_df = join_peaks_with_features(HNNH_frames_df, HNNH_spectrum_df)

    is_max_intensity = get_is_max_intensity_HNNH_frame(HNNH_frames_spectrum_df)
    approx_equal_NH_pair = get_is_approx_equal_NH_pair(tolHN, tolN)

    # Select HNNH peaks with approx equal N1 and N2 frequencies and
    # maximum intensity with the same frames (see is_max_intensity for more details)
    HNNH_peaks_max_intensity_df = \
        HNNH_frames_spectrum_df \
            .loc[lambda row: approx_equal_new(row['N1'], row['N2'], tolN)] \
            .pipe(lambda df: df.loc[df.apply(is_max_intensity, axis=1)]) \
            .sort_values('peak_index')

    # Form pairs of different HNNH peaks with approx. equal frequencies (see approx_equal_NH_pair for more details)
    HNNH_peak_pairs_df = HNNH_peaks_max_intensity_df \
        .merge(HNNH_frames_spectrum_df
               .rename(columns={"frame1": "frame2", "frame2": "frame1"})
               .sort_values('peak_index'),
               how='inner', suffixes=['_1', '_2'], on=["frame1", "frame2"]) \
        .pipe(lambda df: df.loc[df['peak_index_1'] != df['peak_index_2']]) \
        .pipe(lambda df: df.loc[df.apply(approx_equal_NH_pair, axis=1)])

    # Select pairs of HNNH frames with minimum NH_distance and make sure that each frame is in a unique pair
    # (note that both orderings of pairs are always present in HNNH_peak_pairs_df so it is sufficient to remove
    # duplicates in peak_index_1 and peak_index_2 separately
    HNNH_peak_pairs_min_cond_distance_unique_df = \
        HNNH_peak_pairs_df \
            .pipe(lambda df: df.assign(conditional_distance=df.apply(HNNH_pair_compute_NH_distance, axis=1))) \
            .sort_values('conditional_distance') \
            .drop_duplicates(subset=['peak_index_1'], keep='first') \
            .drop_duplicates(subset=['peak_index_2'], keep='first')

    return HNNH_peak_pairs_min_cond_distance_unique_df \
               .loc[:, ['peak_index_1', 'peak_index_2', 'conditional_distance']] \
        .reset_index(drop=True)
