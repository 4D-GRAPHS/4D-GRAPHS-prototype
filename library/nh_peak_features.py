from functools import partial

import pandas as pd
import logging

from commons.flow_control_enums import NHPeakClosenesMeasure, NHPeakDistanceMeasure
from library.peak_distance_measures.NH_peaks_closenes_conditions import NH_absolute_differences_thresholded
from library.peak_distance_measures.NH_peaks_distance_measures import euclidean_peak_distance, manhattan_peak_distance

lg = logging.getLogger(__name__)


def _compute_NH_frames_on_df(NH_peaks_df, HSQC_peaks_df, NH_distance_measure, NH_closeness_measure):
    close_HSQC_frames_boolean_df = NH_peaks_df.apply(lambda NH_peak:
                                                     (HSQC_peaks_df.apply(partial(NH_closeness_measure, NH_peak),
                                                                          axis=1)),
                                                     axis=1)

    NH_peaks_not_too_far_from_HSQC_mask = close_HSQC_frames_boolean_df.apply(lambda row: row.any(), axis=1)

    lg.warning(
        "The following peak indices will be removed from frames since they are not close enough "
        "to any HSQC peaks (in NH components) : " + str(
            NH_peaks_df[~ NH_peaks_not_too_far_from_HSQC_mask]['peak_index'].to_list()))

    NH_peaks_df = NH_peaks_df[NH_peaks_not_too_far_from_HSQC_mask]
    close_HSQC_frames_boolean_df = close_HSQC_frames_boolean_df[NH_peaks_not_too_far_from_HSQC_mask]

    closest_NH_distance_HSQC_frame_index_df = NH_peaks_df.apply(lambda HCNH_peak:
                                                                (HSQC_peaks_df[
                                                                     close_HSQC_frames_boolean_df.loc[HCNH_peak.name]]
                                                                 .apply(partial(NH_distance_measure, HCNH_peak),
                                                                        axis=1))
                                                                .idxmin(), axis=1)

    number_of_close_HSQC_frames_df = close_HSQC_frames_boolean_df.apply(lambda x: x.sum(), axis=1)

    first_close_HSQC_frame_df = close_HSQC_frames_boolean_df.apply(lambda x: x[x].index[0], axis=1)

    d = pd.DataFrame({'closest': closest_NH_distance_HSQC_frame_index_df, 'no_close': number_of_close_HSQC_frames_df,
                      'first_close': list(first_close_HSQC_frame_df)})

    HSQC_frame_numbers_df = d.apply(lambda x: x['first_close'] if x['no_close'] == 1 else x['closest'], axis=1)

    return pd.DataFrame({'peak_index': NH_peaks_df['peak_index'],
                         'frame': HSQC_frame_numbers_df.apply(lambda num: HSQC_peaks_df['frame'][num])})


# INTERFACE

def compute_NH_frames_on_df(HCNH_spectrum_df, HSQC_spectrum_df,
                            HCNH_frames_N_SCALING_FACTOR, HCNH_frames_N_BOUND, HCNH_frames_H_BOUND,
                            HCNH_frames_NH_distance_measure_name, HCNH_frames_NH_closenes_measure_name):
    NH_distance_measures = {
        NHPeakDistanceMeasure.manhattan: manhattan_peak_distance(HCNH_frames_N_SCALING_FACTOR),
        NHPeakDistanceMeasure.euclidean: euclidean_peak_distance(HCNH_frames_N_SCALING_FACTOR)
    }

    NH_closeness_measures = {
        NHPeakClosenesMeasure.absolute_differences_thresholded: NH_absolute_differences_thresholded(
            HCNH_frames_N_BOUND, HCNH_frames_H_BOUND)
    }

    return _compute_NH_frames_on_df(
        HCNH_spectrum_df, HSQC_spectrum_df,
        NH_distance_measures[HCNH_frames_NH_distance_measure_name],
        NH_closeness_measures[HCNH_frames_NH_closenes_measure_name])
