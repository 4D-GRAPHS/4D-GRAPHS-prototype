import pandas as pd
from functools import reduce
from operator import mul


# %%
def select_HCNH_tuples(HCNH_ftuples_df, hist_df, number_of_selected, remove_singlets):
    HCNH_ftuples_clean_df = HCNH_ftuples_df.copy(deep=True)

    HCNH_ftuples_df['variable'] = HCNH_ftuples_df.acid.str.cat(HCNH_ftuples_df.atom, sep='_')

    HCNH_ftuples_dims_df = HCNH_ftuples_df['tuple_index'].groupby(HCNH_ftuples_df['tuple_index']).count()

    if remove_singlets:
        HCNH_ftuples_non_singlets_index = HCNH_ftuples_dims_df[HCNH_ftuples_dims_df > 1].index
        HCNH_ftuples_filtered_singlets = HCNH_ftuples_df.set_index('tuple_index').loc[
            HCNH_ftuples_non_singlets_index].reset_index()
    else:
        HCNH_ftuples_filtered_singlets = HCNH_ftuples_df

    # %%
    hist_cols = [col for col in hist_df.columns if 'hist' in col]
    hist_vertical = pd.melt(hist_df, id_vars=['peak_index'], value_vars=hist_cols)

    hist_vertical['variable'] = hist_vertical.variable.str.strip('hist_')

    # %%

    tuples_with_hist_vals = HCNH_ftuples_filtered_singlets.set_index(['peak_index', 'variable']).join(
        hist_vertical.set_index(['peak_index', 'variable'])).reset_index()

    tuples_with_hist_vals.sort_values('tuple_index')

    # %%

    weighted_tuples = tuples_with_hist_vals.groupby(['acid', 'frame']).apply(lambda frame:
                                                                             frame.groupby('tuple_index').apply(
                                                                                 lambda tuple: reduce(mul,
                                                                                                      tuple['value'])))

    selected_tuples_index = weighted_tuples.sort_values(ascending=False).groupby(['acid', 'frame']).head(
        number_of_selected).index

    # %%

    return HCNH_ftuples_clean_df.set_index(['acid', 'frame', 'tuple_index']).loc[selected_tuples_index] \
        .sort_values('tuple_index').reset_index()
