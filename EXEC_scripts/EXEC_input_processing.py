import io
import pandas as pd
import logging

lg = logging.getLogger(__name__)

from library.input_processing.input_transform import HCNH_input_transform, HNNH_df_input_transform, HSQC_input_transform
from library.input_processing.HSQC_input_cleanup import HSQC_input_cleanup
from commons.EXEC_caching import EXEC_caching_decorator


def EXEC_HCNH_input_transform(HCNH_sparky_input_file, HCNH_peaks_output_csv):
    lg.info("Transforming curated HCNH NOESY from Sparky list to CSV format.")

    HCNH_peaks_df = \
        pd.read_csv(io.StringIO(''.join(
            [row for row in open(HCNH_sparky_input_file, 'r').readlines()
             if not ('Assignment' in row) or row.strip() == '']
        )),
            delim_whitespace=True,
            names=['assignment', 'HC', 'C', 'N', 'HN', 'intensity'])

    HCNH_peaks_df = HCNH_input_transform(HCNH_peaks_df)
    HCNH_peaks_df.to_csv(HCNH_peaks_output_csv, index=False, sep=",", float_format='%g')

    return HCNH_peaks_df


def EXEC_HSQC_input_transform(HSQC_sparky_input_file, HSQC_peaks_output_csv):
    lg.info("Transforming curated HSQC from Sparky list to CSV format.")

    HSQC_peaks_df = pd.read_csv(HSQC_sparky_input_file,
                                delim_whitespace=True,
                                names=['frame', 'N', 'HN'])

    HSQC_peaks_df = HSQC_input_transform(HSQC_peaks_df)
    HSQC_peaks_df.to_csv(HSQC_peaks_output_csv, index=False, sep=",", float_format='%g')

    return HSQC_peaks_df


def EXEC_HNNH_input_transform(HNNH_sparky_input_file, HNNH_peaks_output_csv):
    lg.info("Transforming curated HNNH NOESY from Sparky list to CSV format.")

    HNNH_peaks_df = \
        pd.read_csv(io.StringIO(''.join(
            [row for row in open(HNNH_sparky_input_file, 'r').readlines()
             if not ('Assignment' in row) or row.strip() == '']
        )),
            delim_whitespace=True,
            names=['assignment', 'HN1', 'N1', 'N2', 'HN2', 'intensity'])

    HNNH_peaks_df = HNNH_df_input_transform(HNNH_peaks_df)
    HNNH_peaks_df.to_csv(HNNH_peaks_output_csv, index=False, sep=",", float_format='%g')

    return HNNH_peaks_df


@EXEC_caching_decorator(lg, "Cleaning HSQC peaks.", '_HSQC_spectrum.csv')
def EXEC_HSQC_input_cleanup(HSQC_peaks_df, protein_sequence_list, STARTING_RESID, rtolHN, rtolN, Settings):
    HSQC_spectrum_df = HSQC_input_cleanup(HSQC_peaks_df, protein_sequence_list, STARTING_RESID, rtolHN, rtolN)
    return HSQC_spectrum_df
