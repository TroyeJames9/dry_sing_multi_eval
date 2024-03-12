# -*- coding: utf-8 -*-

"""


"""

from setting import *
import numpy as np
from dtw import *
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


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


def calculate_cosine_similarity(text1, text2, vectorizer_type=0):
    # 将文本转换为词袋表示
    corpus = [text1, text2]
    if vectorizer_type == 0:
        vectorizer = CountVectorizer()
    elif vectorizer_type == 1:
        vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)
    # print(vectorizer.get_feature_names_out())
    # print(X.toarray())
    # 计算余弦相似度
    similarity_matrix = cosine_similarity(X)
    # 提取相似度值
    similarity_score = similarity_matrix[0, 1]
    return similarity_score
