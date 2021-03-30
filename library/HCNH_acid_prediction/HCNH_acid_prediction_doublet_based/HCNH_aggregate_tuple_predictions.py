import pandas as pd


from library.HCNH_acid_prediction.HCNH_acid_prediction_doublet_based.HCNH_preds_hierarchy_processing import get_pred, hierarchy_to_df
from library.HCNH_acid_prediction.HCNH_acid_prediction_doublet_based.HCNH_compute_acid_frame_to_hist_passing_peak_idxs_df import compute_acid_frame_to_hist_passing_peak_idxs_df

def _create_preds_hierarchy_df_full_arity_tuples(pred_dicts_list, acid_frame_arity_to_idxs_dict):
    preds_hierarchy_doublets = {aa_type: {frame: {tpl: {tpl: get_pred(pred_dicts_list, tpl, frame, aa_type)
                        }
                        for arity, peak_idxs_tpls in arity_dict.items() for tpl in peak_idxs_tpls}
                        for frame, arity_dict in frames_to_idxs_dict.items()}
                        for aa_type, frames_to_idxs_dict in acid_frame_arity_to_idxs_dict.items()}
    return hierarchy_to_df(preds_hierarchy_doublets)


def aggregate_tuple_predictions(HCNH_frames, HCNH_histograms_thresholded, HCNH_spectrum, preds_df):
    acid_frame_to_idxs_df = compute_acid_frame_to_hist_passing_peak_idxs_df(HCNH_frames,
                                                                            HCNH_histograms_thresholded,
                                                                            HCNH_spectrum)
    hierarchy_df = _create_preds_hierarchy_df_full_arity_tuples(preds_df.set_index(["frame", "acid", "tpl_tag"]), acid_frame_to_idxs_df)

    df = pd.DataFrame.from_dict(hierarchy_df, orient="index")
    df.index.names = ["frame", "acid", "tpl", "subtpl"]
    return df
