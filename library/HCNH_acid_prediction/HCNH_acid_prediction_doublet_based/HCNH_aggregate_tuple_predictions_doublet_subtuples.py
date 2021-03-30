from library.HCNH_acid_prediction.HCNH_acid_prediction_doublet_based.HCNH_preds_hierarchy_processing import get_pred, hierarchy_to_df
import pandas as pd
import itertools as it
from library.HCNH_acid_prediction.HCNH_acid_prediction_doublet_based.HCNH_compute_acid_frame_to_hist_passing_peak_idxs_df import compute_acid_frame_to_hist_passing_peak_idxs_df

def _create_preds_hierarchy_df_doublets(preds_df, acid_frame_arity_to_idxs_dict):
    preds_hierarchy_doublets = {aa_type: {frame: {tpl: {subtpl: get_pred(preds_df, subtpl, frame, aa_type)
                        for subtpl in it.combinations(tpl, min(2, len(tpl)))}
                        for arity, peak_idxs_tpls in arity_dict.items() for tpl in peak_idxs_tpls}
                        for frame, arity_dict in frames_to_idxs_dict.items()}
                        for aa_type, frames_to_idxs_dict in acid_frame_arity_to_idxs_dict.items()}
    return hierarchy_to_df(preds_hierarchy_doublets)


def HCNH_aggregate_tuple_predictions_doublet_subtuples(HCNH_frames, HCNH_histograms_thresholded, HCNH_spectrum, preds_df):
    acid_frame_to_idxs_df = compute_acid_frame_to_hist_passing_peak_idxs_df(HCNH_frames,
                                                                            HCNH_histograms_thresholded,
                                                                            HCNH_spectrum)
    hierarchy_df_doublets = _create_preds_hierarchy_df_doublets(preds_df.set_index(["frame", "acid", "tpl_tag"]), acid_frame_to_idxs_df)

    df = pd.DataFrame.from_dict(hierarchy_df_doublets, orient="index")
    df.index.names = ["frame", "acid", "tpl", "subtpl"]
    return df

