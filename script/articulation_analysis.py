# -*- coding: utf-8 -*-
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


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


def kmeanCatogery(score_dir_list, cat_num):
    score_list = [value for dictionary in score_dir_list for value in dictionary.values()]
    scores = np.array(score_list)
    kmeans_model = KMeans(n_clusters=cat_num)
    kmeans_model.fit(scores.reshape(-1, 1))
    labels = kmeans_model.labels_
    silhouette_avg = silhouette_score(scores.reshape(-1, 1), labels)
    print("Cluster Centers:", kmeans_model.cluster_centers_)
    print(silhouette_avg)
    return labels
