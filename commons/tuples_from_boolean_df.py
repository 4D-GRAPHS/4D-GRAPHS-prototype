import numpy as np
import pandas as pd


def _get_lists_of_row_indices_of_True_from_columns_of_boolean_df(boolean_df):
    return [list(np.where(boolean_df.values.T[col])[0]) for col in range(boolean_df.shape[1])]


def _get_all_tuples_recursive(l_in, l_out, l_out_index, l_buff, index):
    l = []
    while l == [] and l_in:
        l, l_in = l_in[0], l_in[1:]
        index = index + 1

    if not l_in and l == []:
        if l_out:
            return l_buff + [(l_out, l_out_index)]
        else:
            return l_buff

    l_buff = _get_all_tuples_recursive(l_in, l_out, l_out_index, l_buff, index)

    for i in l:
        if i not in l_out:
            l_buff = _get_all_tuples_recursive(l_in, l_out + [i], l_out_index + [index], l_buff, index)

    return l_buff


def _get_all_tuples(peaks):
    return _get_all_tuples_recursive(peaks, [], [], [], -1)


# %%

def _get_all_tuples_of_given_length_recursive(l_in, l_out, l_out_index, l_buff, index, length):
    l = []
    while l == [] and l_in:
        l, l_in = l_in[0], l_in[1:]
        index = index + 1

    if not l_in and l == []:
        if len(l_out) == length and l_out:
            return l_buff + [(l_out, l_out_index)]
        else:
            return l_buff

    l_buff = _get_all_tuples_of_given_length_recursive(l_in, l_out, l_out_index, l_buff, index, length)

    for i in l:
        if i not in l_out:
            l_buff = _get_all_tuples_of_given_length_recursive(l_in, l_out + [i],
                                                               l_out_index + [index],
                                                               l_buff,
                                                               index,
                                                               length)

    return l_buff


def _get_all_tuples_of_given_length(peaks, length):
    return _get_all_tuples_of_given_length_recursive(peaks, [], [], [], -1, length)


# %%

def _get_max_tuples_recursive(l_in, l_out, l_out_index, l_buff, index, max_len):
    l = []
    while l == [] and l_in:
        l, l_in = l_in[0], l_in[1:]
        index = index + 1

    if not l_in and l == []:
        if len(l_out) >= max_len and l_out:
            return l_buff + [(l_out, l_out_index)], len(l_out)
        else:
            return l_buff, max_len

    l_buff, max_len_rec = _get_max_tuples_recursive(l_in, l_out, l_out_index, l_buff, index, max_len)
    max_len = max(max_len, max_len_rec)

    for i in l:
        if i not in l_out:
            l_buff, max_len_rec = _get_max_tuples_recursive(l_in, l_out + [i], l_out_index + [index], l_buff, index,
                                                            max_len)
            max_len = max(max_len, max_len_rec)

    return l_buff, max_len


def _get_max_tuples(peaks):
    tuples, max_len = _get_max_tuples_recursive(peaks, [], [], [], -1, 0)
    return [t for t in tuples if len(t[0]) == max_len]


# INTERFACE

# For a given dataframe with boolean values computes a list of pairs of lists of row and column indices giving
# "maximum paths" through True values where no column nor row is repeated. (rows and columns are counted from 0)
#
# Example:
# True   False  True   True
# True   True   False  False
# False  True   False  True
#
# We get
# [([1, 0, 2], [1, 2, 3]),
#  ([0, 1, 2], [0, 1, 3]),
#  ([1, 0, 2], [0, 2, 3]),
#  ([1, 2, 0], [0, 1, 3]),
#  ([1, 2, 0], [0, 1, 2])]
#
# Here ([1, 0, 2], [1, 2, 3]) means go through
# 1. row in the 1. column, 0. row in 2. column, 2. row in 3. column
# ([1, 2, 0], [0, 1, 3]) means go through
# 1. row in the 0. column, 2. row in 1. column, 0. row in 3. column

def get_max_tuples(boolean_df):
    return _get_max_tuples(_get_lists_of_row_indices_of_True_from_columns_of_boolean_df(boolean_df))


# This gives just the row indices (as computed by get_max_tuples above)

def get_max_tuples_row_indices(boolean_df):
    max_tuples = get_max_tuples(boolean_df)
    return [pair[0] for pair in max_tuples]


# This gives all paths as described above, not just those of maximum length

def get_all_tuples(boolean_df):
    return _get_all_tuples(_get_lists_of_row_indices_of_True_from_columns_of_boolean_df(boolean_df))


# This gives exactly the paths of the given length
# get_all_tuples_of_given_length(boolean_df, length) ==
#   [tuple for tuple in get_all_tuples(boolean_df) if len(tuple) == length]

def get_all_tuples_of_given_length(boolean_df, length):
    return _get_all_tuples_of_given_length(_get_lists_of_row_indices_of_True_from_columns_of_boolean_df(boolean_df),
                                           length)


# ******************************************************************************************************************
# TESTS

df1 = pd.DataFrame([])

df2 = pd.DataFrame([
    [True, False],
    [False, True]
])

df3 = pd.DataFrame([
    [True, False],
    [True, False]
])

df4 = pd.DataFrame([
    [True, False, True]
])

df5 = pd.DataFrame([
    [True, False, True, False],
    [False, False, True, True],
    [True, False, False, True]
])


def test_get_lists_of_row_indices_of_True_from_columns_of_boolean_df():
    assert _get_lists_of_row_indices_of_True_from_columns_of_boolean_df(df1) == []

    assert _get_lists_of_row_indices_of_True_from_columns_of_boolean_df(df2) == [[0], [1]]

    assert _get_lists_of_row_indices_of_True_from_columns_of_boolean_df(df3) == [[0, 1], []]

    assert _get_lists_of_row_indices_of_True_from_columns_of_boolean_df(df4) == [[0], [], [0]]

    assert _get_lists_of_row_indices_of_True_from_columns_of_boolean_df(df5) == [
        [0, 2],
        [],
        [0, 1],
        [1, 2]
    ]


def test_get_all_tuples():
    assert get_all_tuples(df1) == []

    assert sorted(get_all_tuples(df2)) == sorted([
        ([0], [0]),
        ([1], [1]),
        ([0, 1], [0, 1])
    ])

    assert sorted(get_all_tuples(df3)) == sorted([
        ([0], [0]),
        ([1], [0])
    ])

    assert sorted(get_all_tuples(df4)) == sorted([
        ([0], [0]),
        ([0], [2])
    ])

    assert sorted(get_all_tuples(df5)) == sorted([([1], [3]),
                                                  ([2], [3]),
                                                  ([0], [2]),
                                                  ([0, 1], [2, 3]),
                                                  ([0, 2], [2, 3]),
                                                  ([1], [2]),
                                                  ([1, 2], [2, 3]),
                                                  ([0], [0]),
                                                  ([0, 1], [0, 3]),
                                                  ([0, 2], [0, 3]),
                                                  ([0, 1], [0, 2]),
                                                  ([0, 1, 2], [0, 2, 3]),
                                                  ([2], [0]),
                                                  ([2, 1], [0, 3]),
                                                  ([2, 0], [0, 2]),
                                                  ([2, 0, 1], [0, 2, 3]),
                                                  ([2, 1], [0, 2])])


def test_get_all_tuples_of_given_length():
    assert get_all_tuples_of_given_length(df1, 1) == []

    assert sorted(get_all_tuples_of_given_length(df2, 1)) == sorted([
        ([0], [0]),
        ([1], [1])
    ])

    assert sorted(get_all_tuples_of_given_length(df2, 2)) == sorted([
        ([0, 1], [0, 1])
    ])

    assert sorted(get_all_tuples_of_given_length(df3, 1)) == sorted([
        ([0], [0]),
        ([1], [0])
    ])

    assert sorted(get_all_tuples_of_given_length(df3, 2)) == []

    assert sorted(get_all_tuples_of_given_length(df4, 1)) == sorted([
        ([0], [0]),
        ([0], [2])
    ])

    assert sorted(get_all_tuples_of_given_length(df4, 2)) == []

    assert sorted(get_all_tuples_of_given_length(df5, 3)) == sorted([
        ([0, 1, 2], [0, 2, 3]),
        ([2, 0, 1], [0, 2, 3])
    ])


def test_get_max_tuples():
    assert get_max_tuples(df1) == []

    assert get_max_tuples(df2) == [
        ([0, 1], [0, 1])
    ]

    assert sorted(get_max_tuples(df3)) == sorted([
        ([0], [0]),
        ([1], [0])
    ])

    assert sorted(get_max_tuples(df4)) == sorted([
        ([0], [0]),
        ([0], [2])
    ])

    assert sorted(get_max_tuples(df5)) == sorted([
        ([0, 1, 2], [0, 2, 3]),
        ([2, 0, 1], [0, 2, 3])
    ])