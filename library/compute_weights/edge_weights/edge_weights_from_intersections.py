import pandas as pd


def weights_from_intersections(HCNH_common_peaks_count_df, HCNH_intersections_df, max_intersection_val):
    df = pd.merge(HCNH_common_peaks_count_df, HCNH_intersections_df,
                  on=["source_frame", "target_frame"])[["scaled_intersection", "source_frame", "target_frame"]]
    df.loc[:, "scaled_intersection"] = max_intersection_val * df["scaled_intersection"] / df[
        "scaled_intersection"].max()
    return df.rename(columns={"scaled_intersection": "weight"})