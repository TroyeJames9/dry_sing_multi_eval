# -*- coding: utf-8 -*-

"""

此模块主要用于处理音频信号并提取每个单词的基频特征。主要包括两个核心函数：
1. `calAudioFreq`：利用Librosa库中的Pyin算法估算音频中的基频及其对应时间戳。
2. `getPerWordFeat`：结合单词起止时间和全局基频信息，计算每个字在有效发音区间内的基频特征。

pyin算法相关资料：
https://librosa.org/doc/latest/generated/librosa.pyin.html#librosa.pyin
"""

from setting import *
import numpy as np
import librosa


def calAudioFreq(
    reduced_noise: np.ndarray,  # 输入参数：经过降噪处理后的音频信号数组
    sr: int,  # 输入参数：音频的采样率
    fmax: float = 2093.0,  # 输入参数：最大估计基音频率，默认值为2093.0Hz
    fmin: float = 65.0  # 输入参数：最小估计基音频率，默认值为65.0Hz
) -> tuple:  # 函数返回类型：一个包含两个元素（基频列表和时间戳列表）的元组

    """
    使用Librosa库中的Pyin算法来估计音频各时刻的基音频率，并生成一个元组，
    元组中包括基于这些估计得到的基频列表以及每个基频所对应的时间戳列表。

    参数：
    reduced_noise:
        要进行基音频率分析的预处理过的音频信号数据。
    sr：
        音频的采样率，用于正确计算频率和时间戳。
    fmax：
        搜索基音频率的上限，默认为2093.0赫兹。
    fmin:
        搜索基音频率的下限，默认为65.0赫兹。

    返回：
        Freq_list：
            计算得出的按时间排序的基音频率列表，以赫兹为单位。
        times_list：
            对应于基频列表中各个频率出现的具体时间戳列表。
    """

    # 使用librosa的pyin方法从音频数据中提取基频频率、语音帧标记（是否发声）以及语音概率
    # 返回三个变量：基频频率列表、语音帧标记列表和语音概率列表
    Freq_list, voiced_flag, voiced_probs = librosa.pyin(
        y=reduced_noise, sr=sr, fmin=fmin, fmax=fmax
    )

    # 使用librosa的times_like函数创建与基频频率列表长度相同的时间戳列表
    times_list = librosa.times_like(Freq_list)

    # 将numpy数组类型的基频频率和时间戳列表转换为Python原生的list类型，以便更通用的数据处理
    Freq_list = Freq_list.tolist()
    times_list = times_list.tolist()

    return Freq_list, times_list


def getPerWordFeat(
    eigen_dict: dict, freq_list: list, times_list: list, crop_percent: float = 0.2
) -> dict:
    """
    根据adjustWordTime输出的单词起止时间和calAudioFreq得到的全局基频信息，
    计算每个字在有效发音区间内的基频特征（如中位数基频）。

    参数：
        eigen_dict(dict)：
            包含单词边界信息的字典，键“eigen_list”内储存每个单词的信息
        freq_list(list)：
            表示整个音频片段基频变化的列表
        times_list(list)：
            对应于基频列表的连续时间戳列表
        crop_percent(float)：
            指定从每个单词完整发音区间两侧裁剪的比例，默认为0.2
    返回：
        rs_dict(dict)：
            结构化字典，其中"eigen_list"键下的列表包含每个字的基频特征，结构如下：
                word(str): 单词内容
                eigen(dict):
                    start_time(float): 单词开始时间
                    end_time(float): 单词结束时间
                    times(float): 裁剪后有效的发音持续时间
                    freq(float): 计算得到的该单词的代表性基频值
    """

    # 获取存储了每个单词信息的列表
    eigen_list = eigen_dict["eigen_list"]

    # 遍历所有单词
    for i in range(len(eigen_list)):

        # 获取当前单词的信息字典
        item = eigen_list[i]["eigen"]

        # 计算单词的完整发音持续时间
        times = item["end_time"] - item["start_time"]

        # 根据crop_percent裁剪发音区间
        if times > 0.1:
            seg_start_time = item["start_time"] + times * crop_percent
            seg_end_time = item["end_time"] - times * crop_percent
        else:
            # 如果单词发音时间过短，则使用完整的发音区间
            seg_start_time = item["start_time"]
            seg_end_time = item["end_time"]

        # 筛选出处于裁剪发音区间内的基频频率索引
        indices = [
            index
            for index, time in enumerate(times_list)
            if seg_start_time <= time <= seg_end_time
        ]

        # 获取这些索引对应的非缺失基频值
        freq_seq = [
            freq_list[index] for index in indices if not np.isnan(freq_list[index])
        ]

        # 若未找到匹配的基频值，尝试使用完整发音区间内的基频值
        if not freq_seq:
            indices = [
                index
                for index, time in enumerate(times_list)
                if item["start_time"] <= time <= item["end_time"]
            ]
            freq_seq = [
                freq_list[index] for index in indices if not np.isnan(freq_list[index])
            ]

        # 如果找到了至少一个有效的基频值，计算代表性基频值（这里使用中位数）
        if freq_seq:
            item["freq"] = round(np.median(freq_seq), 3)  # 添加中位数基频到单词信息中
            item["times"] = round(times, 4)  # 添加有效发音持续时间到单词信息中
        else:
            # 如果没有找到任何有效基频值，移除该单词条目
            eigen_list[i] = 0

    # 过滤出仍包含有效信息的字典条目
    eigen_dict["eigen_list"] = [item for item in eigen_list if isinstance(item, dict)]

    # 返回更新后的字典
    return eigen_dict
