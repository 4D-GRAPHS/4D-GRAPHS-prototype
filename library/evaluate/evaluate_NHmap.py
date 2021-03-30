import pandas as pd
from commons.signature_processing_utils import is_sidechain, split_AAIG_signature_both_directions
import logging

lg = logging.getLogger(__name__)


def _get_resid_from_frame_signature(frame_signature):
    """
    Get the residue ID from the frame signature.
    """
    return int(split_AAIG_signature_both_directions(frame_signature)[0][1:])


def evaluate_mapped_frame(row):
    # TODO: ask Jiri what to do with PRO frames.
    if row["frame"].startswith("DUMMY"):
        return "UNASSIGNED"
    elif row["frame"].startswith("PRO"):
        return "PROLINE"
    elif not is_sidechain(row["frame"]) \
            and row["frame"][0] == row["predicted_aatype"] \
            and _get_resid_from_frame_signature(row["frame"]) == row["predicted_resid"]:
        return "CORRECT"
    else:
        return "WRONG"


def evaluate_NHmap(NHmap_csv, protein_sequence_list, start_resid):
    NHmap_df = pd.read_csv(NHmap_csv)

    # Calculate and print statistics
    NHmap_df["predicted_resid"] = NHmap_df["sequence_rank"].apply(lambda rank: rank + start_resid)
    NHmap_df["predicted_aatype"] = NHmap_df["sequence_rank"].apply(lambda rank: protein_sequence_list[rank])
    stats = NHmap_df.apply(lambda r: evaluate_mapped_frame(r), axis=1).values.tolist()
    CORRECT, WRONG, UNASSIGNED, PROLINES, COVERAGE = \
        stats.count("CORRECT"), stats.count("WRONG"), stats.count("UNASSIGNED"), stats.count("PROLINE"), \
        100.0 * (stats.count("CORRECT") + stats.count("WRONG")) / len(protein_sequence_list)
    lg.info("CORRECT=%i , WRONG=%i , UNASSIGNED=%i , PROLINES=%i , COVERAGE=%.2f %%" %
            (CORRECT, WRONG, UNASSIGNED, PROLINES, COVERAGE))
    lg.info("NH-mapping evaluation:\nCORRECT=%i , WRONG=%i , UNASSIGNED=%i , PROLINES=%i , COVERAGE=%.2f %%" %
            (CORRECT, WRONG, UNASSIGNED, PROLINES, COVERAGE))

    return CORRECT, WRONG, UNASSIGNED, PROLINES, COVERAGE
