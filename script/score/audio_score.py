# -*- coding: utf-8 -*-

"""


"""

from setting import *
import numpy as np
from dtw import *


def z_score_normalization(data: list):
    mean = np.mean(data)
    std = np.std(data)
    normalized_data = (data - mean) / std

    return normalized_data


def useDtw(asr_list: list, org_list: list, dist_method: str = "euclidean", is_n: bool = True):
    if is_n:
        asr_list = z_score_normalization(asr_list)
        org_list = z_score_normalization(org_list)
    dtw_rs = dtw(asr_list, org_list, dist_method=dist_method)
    dtw_n = dtw_rs.normalizedDistance

    return dtw_n
