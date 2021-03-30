aa_names_code3 = ["ALA", "ARG", "ASN", "ASP", "CYS", "GLU", "GLN", "GLY", "HIS", "ILE", "LEU", "LYS", "MET", "PHE",
                  "PRO", "SER",
                  "THR", "TRP", "TYR", "VAL"]
aa_names_code1 = ["A", "R", "N", "D", "C", "E", "Q", "G", "H", "I", "L", "K", "M", "F", "P", "S", "T", "W", "Y", "V"]
aa1to3_dict = {c1: c3 for c1, c3 in zip(aa_names_code1, aa_names_code3)}
aa3to1_dict = {c3: c1 for c3, c1 in zip(aa_names_code3, aa_names_code1)}

aatype_maxH_C_pairs_dict = {
    "ALA": 2,
    "ARG": 7,
    "ASP": 3,
    "ASN": 3,
    "CYS": 3,
    "GLU": 5,
    "GLN": 5,
    "GLY": 2,
    "HIS": 3,
    "ILE": 6,
    "LEU": 6,
    "LYS": 9,
    "MET": 5,
    "PHE": 3,
    "PRO": 7,  # Prolines are not detected by the method at position "i" due to lack of HN hydrogen
    "SER": 3,
    "THR": 3,
    "TRP": 3,
    "TYR": 3,
    "VAL": 4
}

aatype_max_H_C_pairs_no_methylenes_dict = {
    'ALA': 2,
    'ARG': 4,
    'ASN': 2,
    'ASP': 2,
    'CYS': 2,
    'GLN': 3,
    'GLU': 3,
    'GLY': 1,
    'HIS': 2,
    'ILE': 5,
    'LEU': 5, # 4?
    'LYS': 5,
    'MET': 4,
    'PHE': 2,
    'PRO': 4,
    'SER': 2,
    'THR': 3,
    'TRP': 2,
    'TYR': 2,
    'VAL': 4 # 3?
}

arity_to_name_dict = {
    1: "singlets",
    2: "doublets",
    3: "triplets",
    4: "quadruplets",
    5: "pentaplets"
}
methylenes = [
    'ARG_CB', 'ARG_CG', 'ARG_CD', 'ASN_CB', 'ASP_CB', 'CYS_CB', 'GLN_CB', 'GLN_CG', 'GLU_CB', 'GLU_CG',
    'GLY_CA', 'HIS_CB', 'ILE_CG1', 'LEU_CB', 'LYS_CB', 'LYS_CG', 'LYS_CD', 'LYS_CE',
    'MET_CB', 'MET_CG', 'PHE_CB', 'PRO_CB', 'PRO_CG', 'PRO_CD',
    'SER_CB', 'TRP_CB', 'TYR_CB'
]