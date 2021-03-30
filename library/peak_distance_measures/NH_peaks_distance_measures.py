def euclidean_peak_distance(N_scaling_factor):
    def peak_distance_measure(NH_peak_1, NH_peak_2):
        return (abs((N_scaling_factor * NH_peak_1['N']) - (N_scaling_factor * NH_peak_2['N']))) ** 2 + \
               abs(NH_peak_1['HN'] - NH_peak_2['HN']) ** 2

    return peak_distance_measure


def manhattan_peak_distance(N_scaling_factor):
    def peak_distance_measure(NH_peak_1, NH_peak_2):
        return (abs((N_scaling_factor * NH_peak_1['N']) - (N_scaling_factor * NH_peak_2['N']))) + \
               abs(NH_peak_1['HN'] - NH_peak_2['HN'])

    return peak_distance_measure
