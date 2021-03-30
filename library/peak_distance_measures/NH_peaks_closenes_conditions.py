def NH_absolute_differences_thresholded(N_threshold, H_threshold):
    def closeness_condition(NH_peak1, NH_peak2):
        return (abs(round(NH_peak1.N, 3) - round(NH_peak2.N, 3)) <= N_threshold) and \
               (abs(round(NH_peak1.HN, 3) - round(NH_peak2.HN, 3)) <= H_threshold)

    return closeness_condition
