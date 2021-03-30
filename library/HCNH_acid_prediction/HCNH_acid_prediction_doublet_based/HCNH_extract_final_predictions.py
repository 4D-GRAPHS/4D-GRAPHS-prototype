
import pandas as pd
from commons.bio_nmr_constants import aatype_max_H_C_pairs_no_methylenes_dict
from commons.bio_nmr_constants import aa_names_code3
import logging

lg = logging.getLogger(__name__)


one_to_three_dict = {
    "A": "ALA",
    "R": "ARG",
    "N": "ASN",
    "D": "ASP",
    "C": "CYS",
    "Q": "GLN",
    "E": "GLU",
    "G": "GLY",
    "H": "HIS",
    "I": "ILE",
    "L": "LEU",
    "K": "LYS",
    "M": "MET",
    "F": "PHE",
    "P": "PRO",
    "S": "SER",
    "T": "THR",
    "W": "TRP",
    "Y": "TYR",
    "V": "VAL",
    "X": "UNK"
}


def _extract_pred_series(df):
    mean_series = df.groupby(["frame", "acid", "tpl"]).mean()
    weighted_mean_series = mean_series.apply(
        lambda row: row[0] * (len(row.name[2]) / aatype_max_H_C_pairs_no_methylenes_dict[row.name[1]]), axis=1)
    pred_series = weighted_mean_series.groupby(["frame", "acid"]).max()

    pred_series = pred_series.groupby('frame').apply(lambda grp: pd.Series(
        dict({aa_type: 0 for aa_type in aa_names_code3}, **{a: v for (f, a), v in grp.to_dict().items()})))
    pred_series.index.names = ["frame", "acid"]
    pred_series.name = "weight"
    return pred_series


def _extract_preds(df, normalize):
    pred_series = _extract_pred_series(df)
    if normalize:
        pred_series = pred_series / pred_series.groupby(["frame"]).sum()
    return pred_series


def _evaluate_final_predictions(pred_df):
    pred_df["real"] = pred_df["frame"].str[0]
    pred_df["real"] = pred_df["real"].map(one_to_three_dict)
    pred_df['rank'] = pred_df[["weight", "frame"]].groupby("frame").rank(ascending=False)
    return pred_df[pred_df['acid'] == pred_df["real"]]["rank"].mean()


def HCNH_extract_final_predictions(pred_hierarchy_df, normalize):
    final_pred_series = _extract_preds(pred_hierarchy_df, normalize).reset_index()
    mean_rank = _evaluate_final_predictions(final_pred_series)
    lg.info("Mean rank is: " + str(mean_rank))
    return final_pred_series


