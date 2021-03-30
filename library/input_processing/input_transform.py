import pandas as pd
import numpy as np


def HCNH_input_transform(HCNH_peaks_df):
    """
    Load Sparky list file into a DataFrame and remove invalid lines.
    """
    # Cast number columns to numeric, even if they contain strings (=invalid lines)
    HCNH_peaks_df[['HC', 'C', 'N', 'HN', 'intensity']] = \
        HCNH_peaks_df[['HC', 'C', 'N', 'HN', 'intensity']] \
            .apply(pd.to_numeric, errors='coerce')  # By setting errors=’coerce’, you’ll transform the non-numeric values into NaN.

    HCNH_peaks_df.dropna(how='any', axis=0, inplace=True)   # remove invalid lines

    HCNH_peaks_df = HCNH_peaks_df.loc[HCNH_peaks_df['intensity'] > 0, :]  # to remove peaks with 0 intensity

    HCNH_peaks_df.insert(0, "peak_index", range(HCNH_peaks_df.shape[0]))

    HCNH_peaks_df = HCNH_peaks_df \
        .sort_values(by="assignment", ascending=False) \
        .drop_duplicates(keep="first", subset=['HC', 'C', 'N', 'HN', 'intensity'])

    HCNH_peaks_df['intensity'] = HCNH_peaks_df['intensity'].abs()

    # Convert assignments like 'A100HA-CA-N-H' to 'A100HA-CA-A100N-H'
    # TODO: position to be reconsidered - maybe this belongs to a later stage in the pipeline.
    HCNH_peaks_df.loc[HCNH_peaks_df['assignment'].str.match("^[A-Z][0-9]+.+\-[XN][DE12]*\-[XH][DE12]*$"), 'assignment'] = \
        HCNH_peaks_df[HCNH_peaks_df['assignment'].str.match("^[A-Z][0-9]+.+\-[XN][DE12]*\-[XH][DE12]*$")]['assignment'] \
            .str \
            .extract("^([A-Z][0-9]+)(.+)\-([XN][DE12]*\-[XH][DE12]*)$") \
            .rename({0: 'residue_assignment', 1: 'CH_assignment', 2: 'NH_assignment'}, axis=1) \
            .apply(
            lambda r: "%s%s-%s%s" % (r.residue_assignment, r.CH_assignment, r.residue_assignment, r.NH_assignment),
            axis=1)

    return HCNH_peaks_df.round({'HC': 3, 'C': 3, 'N': 3, 'HN': 3})


def HSQC_input_transform(HSQC_peaks_df):
    """
    Load Sparky list file into a DataFrame and remove invalid lines.
    """
    # Cast number columns to numeric, even if they contain strings (=invalid lines)
    HSQC_peaks_df[['N', 'HN']] = \
        HSQC_peaks_df[['N', 'HN']].apply(pd.to_numeric,
                                         errors='coerce')  # By setting errors=’coerce’, you’ll transform the non-numeric values into NaN.
    HSQC_peaks_df.dropna(how='any', axis=0, inplace=True)  # remove invalid lines

    HSQC_peaks_df.insert(0, "peak_index", range(HSQC_peaks_df.shape[0]))

    HSQC_peaks_df = \
        HSQC_peaks_df \
            .sort_values(by="frame", ascending=False) \
            .drop_duplicates(keep="first", subset=['N', 'HN'])

    return HSQC_peaks_df.round({'N': 3, 'HN': 3})


def HNNH_df_input_transform(HNNH_peaks_df, index_peaks=True):
    """
    Remove invalid lines & rows from HNNH DataFrame. Works for both assigned and unassigned HNNH spectra.
    """
    HNNH_peaks_df.dropna(how='all', axis=1, inplace=True)  # remove 'NaN columns'

    HNNH_peaks_df.columns = ['assignment', 'HN1', 'N1', 'N2', 'HN2', 'intensity']

    # Cast number columns to numeric, even if they contain strings (=invalid lines)
    HNNH_peaks_df[['HN1', 'N1', 'N2', 'HN2', 'intensity']] = \
        HNNH_peaks_df[['HN1', 'N1', 'N2', 'HN2', 'intensity']] \
            .apply(pd.to_numeric, errors='coerce')  # By setting errors=’coerce’, you’ll transform the non-numeric values into NaN.
    HNNH_peaks_df.dropna(how='any', axis=0, inplace=True)   # remove invalid lines

    HNNH_peaks_df['intensity'] = HNNH_peaks_df['intensity'].abs()   # we want only positive intensities

    HNNH_peaks_df = HNNH_peaks_df.loc[HNNH_peaks_df['intensity'] > 0, :]  # to remove peaks with 0 intensity

    if index_peaks:
        HNNH_peaks_df.insert(0, "peak_index", range(HNNH_peaks_df.shape[0]))

    HNNH_peaks_df = HNNH_peaks_df.sort_values(by='assignment', key=lambda assig: assig == '?-?-?-?',
                                              kind='mergesort') \
        .drop_duplicates(subset=['HN1', 'N1', 'N2', 'HN2', 'intensity'], keep='first', inplace=False)

    return HNNH_peaks_df.round({'HΝ1': 3, 'Ν1': 3, 'N2': 3, 'HN2': 3})
