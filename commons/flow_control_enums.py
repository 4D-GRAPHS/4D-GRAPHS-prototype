import enum


class EdgeWeightType(enum.Enum):
    common_peaks_count_0_1 = 1
    intersections = 2


class EdgeAcidWeightType(enum.Enum):
    rf_acid_prediction = 1
    relative_max_tuple_length = 2


class PredictionAlgType(enum.Enum):
    tuples_algorithm = 1
    doublet_based_algorithm = 2


class CommonPeaksAlg(enum.Enum):
    max_tuple_selection = 1
    distance_ordered_tuples = 2


class MethylenesAlg(enum.Enum):
    agglomerative_clustering = 1
    distance_ordering = 2


class NHPeakDistanceMeasure(enum.Enum):
    manhattan = 1
    euclidean = 2


class NHPeakClosenesMeasure(enum.Enum):
    absolute_differences_thresholded = 1


class TupleKind(enum.Enum):
    max_tuple = 1
    n_tuple = 2
