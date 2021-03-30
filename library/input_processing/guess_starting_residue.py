from commons.signature_processing_utils import is_valid_signature, is_sidechain
import logging

lg = logging.getLogger(__name__)


def guess_starting_residue(HSQC_peaks_df, protein_sequence_list):
    """
        Method that tries to guess the starting resid from the labels present in the HSQC HSQC file.
        The function will return
    """

    labeled_residues_df = HSQC_peaks_df['frame'] \
        .loc[HSQC_peaks_df['frame'].apply(lambda frame: is_valid_signature(frame) and not is_sidechain(frame))] \
        .str.extract("^([ARNDCEQGHILKMFPSTWYV])([0-9]+)N-H$") \
        .rename({0: 'aa_type', 1: 'resid'}, axis=1) \
        .dropna(axis=0) \
        .pipe(lambda df: df.assign(resid=df['resid'].astype(int))) \
        .sort_values(by='resid', ascending=True)

    if labeled_residues_df.shape[0] == 0:
        lg.warning(
            "I could not guess the starting residue number from the labels in the file. Therefore I will relabel ",
            "everything starting from 1. If you want to keep your labels please check again for consistency with the "
            "protein sequence.")
        return None

    existing_resnames = ''.join(list(labeled_residues_df['aa_type']))
    first_resid = labeled_residues_df.iloc[0][1]  # the number in the label with the smallest resid
    existing_resids = [d - first_resid for d in
                       labeled_residues_df['resid']]  # subtract from the labeled resids the first so that
    # they start from 0

    possible_starting_positions = [start_index for start_index in
                                   range(0, len(protein_sequence_list) - max(existing_resids)) if
                                   existing_resnames in
                                   ''.join([protein_sequence_list[i + start_index] for i in existing_resids])]

    if len(possible_starting_positions) == 0:
        lg.warning("I could not guess the starting residue number from the labels in the file. There must "
                   "be a conflict in the residue names you placed and the protein sequence, therefore I will "
                   "relabel everything starting from 1. If you want to keep your labels please check again "
                   "for consistency with the protein sequence.")
        return None

    elif len(possible_starting_positions) == 1:
        lg.warning("I found one possible starting position in the sequence (%i) from "
                   "the labels in the file. Residue numbering starts from %i . Keeping the "
                   "current labels and relabeling all other peaks starting from 'X1N-H', 'X2N-H', etc." %
                   (possible_starting_positions[0], first_resid - possible_starting_positions[0]))
        return first_resid - possible_starting_positions[0]

    elif len(possible_starting_positions) > 1:
        lg.error("ERROR: I found multiple possible starting positions in the sequence "
                 "(%s). I will keep the first, which covers more sequence. "
                 "Residue numbering starts from %s. Keeping the "
                 "current labels and relabeling all other peaks starting from 'X1N-H', 'X2N-H', etc." %
                 (",".join([str(p) for p in possible_starting_positions]),
                  first_resid - possible_starting_positions[0]))
        return first_resid - possible_starting_positions[0]
