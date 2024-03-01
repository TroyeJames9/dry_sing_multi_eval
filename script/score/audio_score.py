# -*- coding: utf-8 -*-

"""


"""

from setting import *
import numpy as np


def z_score_normalization(data: list):
    mean = np.mean(data)
    std = np.std(data)
    normalized_data = (data - mean) / std
    return normalized_data
