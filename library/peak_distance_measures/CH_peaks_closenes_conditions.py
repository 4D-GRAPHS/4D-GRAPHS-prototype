def get_closenes_condition(closenes_condition_name_and_args, C_names=['C', 'C'], H_names=['HC', 'HC']):
    if closenes_condition_name_and_args['name'] == 'C_H_absolute_differences_thresholded':
        def closeness_condition(CH_peak1, CH_peak2):
            return (abs(round(CH_peak1.C, 3) - round(CH_peak2.C, 3)) <= closenes_condition_name_and_args['C_bound']) \
                   and (abs(round(CH_peak1.HC, 3) - round(CH_peak2.HC, 3)) <= closenes_condition_name_and_args[
                'H_bound'])

        return closeness_condition
