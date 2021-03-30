import pandas as pd

def HCNH_find_aromatics(HCNH_spectrum_df, aromatics_Cthreshold):
    return pd.DataFrame(
        {'peak_index': HCNH_spectrum_df['peak_index'],
         'is_aromatic': HCNH_spectrum_df['C']>aromatics_Cthreshold}
    )