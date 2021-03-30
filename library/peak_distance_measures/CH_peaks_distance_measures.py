def get_distance_measure(distance_measure_name_and_args, C_names=['C', 'C'], H_names=['HC', 'HC']):
    if distance_measure_name_and_args['name'] == 'euclidean':
        def distance_measure(CH_peak1, CH_peak2):
            return ((CH_peak1[C_names[0]] - CH_peak2[C_names[1]]) ** 2) + \
                   ((CH_peak1[H_names[0]] - CH_peak2[H_names[1]]) ** 2)

        return distance_measure
