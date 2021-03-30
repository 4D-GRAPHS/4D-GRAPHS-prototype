import logging
lg = logging.getLogger(__name__)

def HCNH_threshold_histograms(HCNH_histograms_df, histogram_threshold):
    hist_columns = [col for col in HCNH_histograms_df.columns if 'hist' in col]

    f = HCNH_histograms_df.apply(
        lambda x: x >= histogram_threshold
        if x.name in hist_columns else x
    )

    lg.debug(f)

    return f[['peak_index'] + hist_columns]