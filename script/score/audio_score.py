# -*- coding: utf-8 -*-

"""

本模块包含多个用于数据分析和处理的函数，涵盖了标准化、相似度计算、聚类等操作。
主要功能包括：
1. 对一维数据进行z-score标准化处理。
2. 计算两个语音特征列表的动态时间规整(DTW)距离。
3. 计算两个文本字符串的余弦相似度。
4. 使用K-means算法对音乐评分数据进行分类。

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
    """
    对输入的一维数据列表执行z-score标准化（也称为标准化得分标准化），
    使得处理后的数据具有均值为0和标准差为1的正态分布特性。

    参数:
        data (list): 待标准化的一维数值列表

    返回:
        normalized_data (list): 经过z-score标准化处理后的新数据列表

    """
    mean = np.mean(data)
    std = np.std(data)
    normalized_data = (data - mean) / std

    return normalized_data


def useDtw(asr_list: list, org_list: list, dist_method: str = "euclidean", is_n: bool = True):
    """
    计算两个语音特征列表（ASR识别结果列表与原始语音特征列表）的动态时间规整(DTW)距离，
    并根据用户需求对输入数据进行z-score标准化处理，最后返回归一化的DTW距离。

    参数:
        asr_list (list): ASR自动语音识别系统输出的语音特征列表
        org_list (list): 原始语音信号的特征列表
        dist_method (str, 默认="euclidean"): DTW计算中使用的距离度量方法，默认为欧式距离
        is_n (bool, 默认=True): 是否对输入数据进行z-score标准化处理

    返回:
        dtw_n (float): 归一化后的DTW距离

    """

    # 如果is_n为True，则对ASR列表和原始列表都进行z-score标准化处理
    if is_n:
        asr_list = z_score_normalization(asr_list)  # 对ASR列表进行标准化
        org_list = z_score_normalization(org_list)  # 对原始列表进行标准化

    # 使用指定的距离度量方法计算两个列表间的DTW距离
    dtw_rs = dtw(asr_list, org_list, dist_method=dist_method)

    # 提取并返回DTW距离的归一化值
    dtw_n = dtw_rs.normalizedDistance

    return dtw_n


def calculate_cosine_similarity(text1: str, text2: str, vectorizer_type: int = 0) -> float:
    """
    计算两个文本字符串的余弦相似度。

    参数:
    - text1 (str): 第一个文本字符串。
    - text2 (str): 第二个文本字符串。
    - vectorizer_type (int): 向量化方法选择，默认为0。0表示使用CountVectorizer（词频统计）；
                            1表示使用TfidfVectorizer（TF-IDF加权）。

    返回:
    - float: 两个文本向量之间的余弦相似度得分，范围在-1到1之间，值越接近1表示相似度越高。

    """

    # 创建一个包含待处理文本的列表
    corpus = [text1, text2]

    # 根据vectorizer_type参数选择相应的文本特征提取器
    if vectorizer_type == 0:
        vectorizer = CountVectorizer()
    elif vectorizer_type == 1:
        vectorizer = TfidfVectorizer()

    # 将文本转化为数值矩阵
    X = vectorizer.fit_transform(corpus)

    # 计算余弦相似度
    similarity_matrix = cosine_similarity(X)

    # 提取相似度值
    similarity_score = similarity_matrix[0, 1]

    return similarity_score


def kmeanCatogery(score_dir_list, cat_num):
    """
    实现K-means算法对音乐评分数据进行分类，并将分类结果存储到字典中。

    分析音乐评分数据（以字典列表形式提供，每个字典代表一首歌及其评分），通过K-means算法将其划分为指定数量（cat_num）的类别，
    并返回一个字典，其中键为歌曲名称，值为对应的类别标签。

    参数：
    - score_dir_list: 一个包含多个字典的列表，每个字典表示一首歌的评分数据，字典的键为歌曲名，值为评分。
    - cat_num: 整数，指定希望将评分数据划分成的类别数目。

    返回：
    - result_dict: 字典类型，键为歌曲名，值为对应歌曲经过K-means聚类后得到的类别标签。
    """
    # 初始化一个空的结果字典，用于存放歌曲名称及其所属类别
    result_dict = {}

    # 将所有歌曲评分数据合并到一个列表中
    score_list = [value for dictionary in score_dir_list for value in dictionary.values()]
    scores = np.array(score_list)

    kmeans_model = KMeans(n_clusters=cat_num)
    kmeans_model.fit(scores.reshape(-1, 1))
    labels = kmeans_model.labels_

    # 打印聚类中心和轮廓系数，评估聚类效果
    print("Cluster Centers:", kmeans_model.cluster_centers_)
    silhouette_avg = silhouette_score(scores.reshape(-1, 1), labels)
    print("Silhouette Coefficient:", silhouette_avg)

    # 遍历原始评分数据字典列表，将歌曲名称和其对应的类别标签添加到结果字典中
    for idx, score_dict in enumerate(score_dir_list):
        # 提取当前字典对应的歌曲名称
        song_name = list(score_dict.keys())[0]
        # 将类别标签存入结果字典，键为歌曲名称，值为类别标签
        result_dict[song_name] = labels[idx]

    # 返回存放了歌曲名称及其类别标签的结果字典
    return result_dict
