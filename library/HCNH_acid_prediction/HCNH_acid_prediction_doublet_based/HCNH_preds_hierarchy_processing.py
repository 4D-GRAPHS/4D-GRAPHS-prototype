import pandas as pd


def get_pred(df, subtpl, frame, aa_type):
    frame = frame.split("__")[0]

    return df.loc[frame, aa_type, subtpl]['weight'].values[0]


def hierarchy_to_df(hierarchy_dict):
    return {(frame, aa_type, tpl, dbl): pd.Series(pred)
                            for aa_type, frames_to_tpls_dict in hierarchy_dict.items()
                            for frame, tpl_dict in frames_to_tpls_dict.items()
                            for tpl, preds in tpl_dict.items()
                            for dbl, pred in preds.items()
                        }