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


# 使用jieba库切词后实现中文句子的余弦相似打分，text文本需传入字符串
def calculate_cosine_jieba(text1, text2, cut_all=False):
    s1_cut = [i for i in jieba.cut(text1, cut_all=cut_all) if i != '' and i != ' ']
    s2_cut = [i for i in jieba.cut(text2, cut_all=cut_all) if i != '' and i != ' ']
    word_set = set(s1_cut).union(set(s2_cut))

    word_dict = dict()
    i = 0
    for word in word_set:
        word_dict[word] = i
        i += 1

    s1_cut_code = [word_dict[word] for word in s1_cut]
    s1_cut_code = [0] * len(word_dict)

    for word in s1_cut:
        s1_cut_code[word_dict[word]] += 1

    s2_cut_code = [word_dict[word] for word in s2_cut]
    s2_cut_code = [0] * len(word_dict)

    for word in s2_cut:
        s2_cut_code[word_dict[word]] += 1

    # 计算余弦相似度
    dot_product = 0
    sq1 = 0
    sq2 = 0
    for i in range(len(s1_cut_code)):
        dot_product += s1_cut_code[i] * s2_cut_code[i]
        sq1 += pow(s1_cut_code[i], 2)
        sq2 += pow(s2_cut_code[i], 2)

    try:
        result = round(float(dot_product) / (math.sqrt(sq1) * math.sqrt(sq2)), 2)
    except ZeroDivisionError:
        result = 0.0

    return result

