import pandas as pd

from commons.signature_processing_utils import is_sidechain, is_valid_signature


def _get_default_frame_labels(number_of_frames, frames_to_exclude=[]):
    return ["X" + str(count + 1) + "NX-HX" for count in range(number_of_frames + len(frames_to_exclude))
            if "X" + str(count + 1) + "NX-HX" not in frames_to_exclude][:number_of_frames]


def _HSQC_clean_up_frame_names(HSQC_spectrum_df, protein_sequence_list, STARTING_RESID):
    """
    This method reads in the {N-H}-HSQC file in sparky list format. If there are labels inside that comply
    with the pattern '[A-Z][0-9]+N-H' (e.g. A13N-H), the script will check if these labels are valid given
    the protein sequence. If yes, it will keep them and rename all other peaks as 'X[0-9]+'. If not, then
    it will ignore all existing labels and relabel all peaks.
    """

    if not STARTING_RESID:
        HSQC_spectrum_df['frame'] = _get_default_frame_labels(HSQC_spectrum_df.shape[0])
        return HSQC_spectrum_df

    # consider labels meeting the conditions as valid labels from the user and relabel the rest of the peaks

    # CASE 1: valid frame labels - leave them as they are
    frame_mask = HSQC_spectrum_df['frame'] \
        .str \
        .extract("^([A-Z])([0-9]+)NX?-HX?$") \
        .rename({0: 'aa_type', 1: 'resid'}, axis=1) \
        .apply(lambda row: (not pd.isnull(row).any()) and
                           (int(row['resid']) - STARTING_RESID < len(protein_sequence_list)) and
                           (row['aa_type'] == protein_sequence_list[int(row['resid']) - STARTING_RESID]), axis=1)

    # CASE 2: labels of sidechain frames - leave labels as they are
    sidechain_frame_mask = HSQC_spectrum_df['frame'].apply(
        lambda frame: is_valid_signature(frame) & is_sidechain(frame))

    # CASE 3 (for Kostas): if the label is of the form "[0-9]+NX?-HX?", then keep it
    # to ease the user in the re-assignment
    special_frame_mask = HSQC_spectrum_df['frame'].str.contains("^[0-9]+NX?-HX?$")

    HSQC_spectrum_df.loc[special_frame_mask, 'frame'] = \
        HSQC_spectrum_df.loc[special_frame_mask, 'frame'] \
            .str \
            .extract("^([0-9]+)NX?-HX?$") \
            .dropna() \
            .apply(lambda group: "X" + group + "NX-HX")[0]

    # CASE 4: The frame label does not have one of the possible format above - a default label will be assigned
    # (X1, X2, X3, etc.) that does not conflict with Kostas' manually assigned labels
    no_label_frame_mask = ~(frame_mask | sidechain_frame_mask | special_frame_mask)

    HSQC_spectrum_df.loc[no_label_frame_mask, 'frame'] = \
        _get_default_frame_labels(sum(no_label_frame_mask),
                                  HSQC_spectrum_df.loc[special_frame_mask, 'frame'].tolist())

    # Detect duplicate frame labels
    frame_label_duplicates = HSQC_spectrum_df['frame'].duplicated()
    if frame_label_duplicates.sum() > 0: raise KeyError("Frame labels %s have been used at least twice" % \
                                                        HSQC_spectrum_df['frame'][frame_label_duplicates])

    return HSQC_spectrum_df


def _HSQC_peaks_overlap(r1, r2, rtolHN, rtolN):
    return (r1["peak_index"] != r2["peak_index"]) and \
           (abs(r1["HN"] - r2["HN"]) <= rtolHN) and \
           (abs(r1["N"] - r2["N"]) <= rtolN)


def _HSQC_detect_peaks_overlaps(HSQC_peaks_df, rtolHN, rtolN):
    overlaps_mask = HSQC_peaks_df.apply(
        lambda r1: HSQC_peaks_df.apply(lambda r2: _HSQC_peaks_overlap(r1, r2, rtolHN, rtolN), axis=1).any(), axis=1)

    if sum(overlaps_mask) > 0:
        raise (Exception("FAIL: the following HSQC peaks overlap almost completely: " +
                         str(HSQC_peaks_df['frame'][overlaps_mask])))


def HSQC_input_cleanup(HSQC_peaks_df, protein_sequence_list, STARTING_RESID, rtolHN=0.005, rtolN=0.015):
    HSQC_peaks_corrected_df = _HSQC_clean_up_frame_names(HSQC_peaks_df, protein_sequence_list, STARTING_RESID)

    _HSQC_detect_peaks_overlaps(HSQC_peaks_corrected_df, rtolHN, rtolN)

    return HSQC_peaks_corrected_df
