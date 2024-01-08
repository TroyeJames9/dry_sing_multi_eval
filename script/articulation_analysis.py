# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


def calculate_cosine_similarity(text1, text2, vectorizer_type=0):
    # 将文本转换为词袋表示
    corpus = [text1, text2]
    if vectorizer_type == 0:
        vectorizer = CountVectorizer()
    elif vectorizer_type == 1:
        vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)
    # 计算余弦相似度
    similarity_matrix = cosine_similarity(X)
    # 提取相似度值
    similarity_score = similarity_matrix[0, 1]
    return similarity_score



