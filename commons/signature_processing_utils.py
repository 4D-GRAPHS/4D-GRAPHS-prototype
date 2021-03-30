import re

import logging
lg = logging.getLogger(__name__)

def replace_alt(text, alt_txtlist, new_txt):
    "Method to do replace multiple alternative texts with one specific text."
    for txt in alt_txtlist:
        text = text.replace(txt, new_txt)
    return text


def remove_NH_suffix(text):
    return replace_alt(text, ['N-H', "ND2-HD21", "ND2-HD22", "NE2-HE21", "NE2-HE22", "NE1-HE1", 'NE-HE', 'NX-HX',
                              'NH', "ND2HD21", "ND2HD22", "NE2HE21", "NE2HE22", "NE1HE1", 'NEHE', 'NXHX'], '')


def split_AAIG_signature_both_directions(AAIG_signature):
    """
    Method to split the AAIG signature into AAIG and amide name. If the signature contains '-' then it will
    return the AAIG name and the amide name with '-'. If not then the returned amide will not contain '-' either.
    :param AAIG_signature:
    :return:
    """
    NHnames = ['NH', 'ND2HD21', 'ND2HD22', 'NE2HE21', 'NE2HE22', 'NEHE', 'NE1HE1', '??', 'NXHX',
               'N-H', 'ND2-HD21', 'ND2-HD22', 'NE2-HE21', 'NE2-HE22', 'NE-HE', 'NE1-HE1', '?-?', 'NX-HX',
               'HN', 'HD21ND2', 'HD22ND2', 'HE21NE2', 'HE22NE2', 'HENE', 'HE1NE1', 'HXNX',
               'H-N', 'HD21-ND2', 'HD22-ND2', 'HE21-NE2', 'HE22-NE2', 'HE-NE', 'HE1-NE1', 'HX-NX'
               ]

    AAIG_signature_strip = AAIG_signature.strip()

    fit = [(AAIG_signature_strip[:-len(NH_name)], NH_name) for NH_name in NHnames if
           AAIG_signature_strip.endswith(NH_name)]

    return fit[0] if fit else ('?', '?')


def reverse_NH_suffix(AAIG_signature):
    """
    For i_AAIG, my naming is "N-HN" while the correct is "HN-N".
    :return:
    """
    AAIG_name, NH_name = split_AAIG_signature_both_directions(AAIG_signature)
    if NH_name == '?':
        return AAIG_signature
    new_NH_name = NH_name.split('-')[1] + "-" + NH_name.split('-')[0]
    return AAIG_name + new_NH_name


def _get_NH_name(AAIG_signature):
    """
    Get the amide name from the AAIG signature.
    :param AAIG_signature:
    :return:
    """
    return split_AAIG_signature_both_directions(AAIG_signature)[1]


def is_sidechain(AAIG_signature):
    """
    Does the given AAIG signature belong to a side chain?
    :param AAIG_signature:
    :return True/False:
    """
    return _get_NH_name(AAIG_signature) in ['ND2HD21', 'ND2-HD21', 'ND2HD22', 'ND2-HD22', 'NE2HE21', 'NE2-HE21',
                                           'NE2HE22', 'NE2-HE22', 'NEHE', 'NE-HE', 'NE1HE1', 'NE1-HE1']

def is_valid_signature(AAIG_signature):
    # TODO: maybe is imperfect.
    return bool(re.match("^[A-Z][0-9]+[XN][DE12]*[XH][DE12]+$", AAIG_signature)) or \
           bool(re.match("^[A-Z][0-9]+[XN][DE12]*\-[XH][DE12]*$", AAIG_signature))


def new_is_valid_signature(AAIG_signature):
    # accepts reverse NH names, is it wrong?
    AAIG_name, NH_name = split_AAIG_signature_both_directions(AAIG_signature)
    return (AAIG_name != '?') and bool(re.match("^[A-Z][0-9]+$", AAIG_name.strip()))