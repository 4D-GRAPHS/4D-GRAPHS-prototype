import pandas as pd

def HCNH_read_precomputed_intersections(precomputed_data_dir, protein):
    return pd.read_csv(precomputed_data_dir + protein + '_connectivities_occupancy_intersection.csv')
