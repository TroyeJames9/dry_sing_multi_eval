# -*- coding: utf-8 -*-

"""模块功能描述

详细描述

"""

from setting import *
import json
import pandas as pd
import numpy as np
import librosa


def audioWordSeg(
    eigen_list: dict = None,
    reduced_noise: np.ndarray = None,
    sr: int = None,
    delay_second: float = 0.13,
    word_time_delay_ahead=0.12,
    word_time_delay_behind=0.1,
) -> dict:
    """按照getWordInfoList的结果列表，以词为单位，将音频时域信息序列进行切割，eg："来"的时间间隔为1.3秒，要获取这个时间间隔内的音频信息。

    参数：
        eigen_list(dict)：
            传入需要提取的JSON文件，字典文件中包括start_time,end_time,word。
        reduced_noise:
            降噪后音频的时域信息。
        sr：
            采样率。
        delay_second:
            延后的原因是科大讯飞识别的延后秒数近似常量，默认为0.15。
        word_time_delay_ahead:
            计算首个字的音长所延后的秒数，多次测试后默认为0.12
        word_time_delay_behind:
            计算最后的字的音长所延后的秒数，多次测试后默认为0.1

    返回：
        eigen_list：
            在传入的JSON文件中，增加了以词为单位的时间间隔和该时间段内的时域信息。eg：
    {'eigen_list': [{'word': '起来',
       'eigen': {'start_time': 13.0,
        'end_time': 14.39,
        'audio_segment': array([ 8.5642641e-05, -5.3360149e-05, -2.1816693e-05, ...,
                2.0035163e-02,  2.3617115e-02,  1.1252311e-02], dtype=float32),
        'times': 1.3900000000000006,
        'word_start_time' :...,
        'word_end_time' :...,}} ,..., {'word'....}]}

    """

    eigen_list = eigen_list["eigen_list"]

    eigen_segments = []  # 用来存储子字典eigen_segment
    """遍历JSON文件中的子字典eigen_list，获取其中的每个词的起始和结束时间，并按时间段进行切割音频，返回出np.ndarray类型"""
    for item in eigen_list:
        # times = item["eigen"]["end_time"] - item["eigen"]["start_time"]
        # times = round(times, 3)
        if len(item["word"]) > 1:
            start_time = round(item["eigen"]["start_time"] + delay_second, 3)
            end_time = round(item["eigen"]["end_time"] + delay_second * 0.4, 3)
            word_start_time = round(
                item["eigen"]["start_time"] + word_time_delay_ahead, 3
            )
            word_end_time = round(item["eigen"]["end_time"] + word_time_delay_behind, 3)
        elif len(item["word"]) == 1:
            start_time = round(item["eigen"]["start_time"] + delay_second * 0.7, 3)
            end_time = round(item["eigen"]["end_time"] + delay_second * 0.6, 3)
            word_start_time = start_time
            word_end_time = end_time
        word = item["word"]
        times = word_end_time - word_start_time
        times = round(times, 3)
        start_time += (end_time - start_time) * 0.1
        end_time -= (end_time - start_time) * 0.1

        # 将时间转换为样本索引
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)

        # 根据样本索引切割时域信号
        audio_segment = reduced_noise[start_sample:end_sample]

        # 构建新的子字典
        eigen_segment = {
            "word": word,
            "eigen": {
                "start_time": start_time,
                "end_time": end_time,
                "seg_seq": audio_segment,
                "times": times,
                "word_start_time": word_start_time,
                "word_end_time": word_end_time,
            },
        }

        eigen_segments.append(eigen_segment)
    eigen_list = {"eigen_list": eigen_segments}

    return eigen_list


def calAudioFreq(
    reduced_noise: np.ndarray, sr: int, fmax: float = 2093.0, fmin: float = 65.0
) -> tuple:
    """使用Pyin算法来估计各时刻的基音频率，生成一个元组，包括基频列表和基频对应的times列表.

    reduced_noise:
        noiseReduce的返回结果。
    sr：
        noiseReduce的返回的采样率。
    fmax：
        估计的最大频率，默认为2093.0。
    fmin:
        估计的最小频率，默认为65.0。

    返回：
        Freq_list：
            基频列表。
        times_list：
            各基频对应的times的列表。
    """
    # Freq_list 以赫兹为单位的基频时间序列。voiced_flag 包含指示帧是否有声的布尔标志的时间序列；voiced_probs 包含帧有声概率的时间序列。
    Freq_list, voiced_flag, voiced_probs = librosa.pyin(
        y=reduced_noise, sr=sr, fmin=fmin, fmax=fmax
    )

    times_list = librosa.times_like(Freq_list)
    Freq_list = Freq_list.tolist()
    times_list = times_list.tolist()
    return Freq_list, times_list


def getWordFreqSeq(word_dict: dict, Freq_list: list, times_list: list) -> dict:
    """传入eigen_list的一个字典元素，根据start_time和end_time将该字典元素对应的歌词的基频序列保存到字典中

    参数：
        word_dict:
            audioWordSeg返回结果中的eigen_list的一个元素，eg：{"word": "起来","eigen": {"seg_seq": null,"times": 2,"start_time": 1.85,"end_time": 3.85 }}。
        Freq_list：
            基频列表，calAudioFreq的返回结果。
        times_list：
            各基频对应的times的列表，calAudioFreq的返回结果。


    返回：
        rs_dict:
            返回一个新的字典，形如：{"word":xx, "eigen":{"seg_seq":xx,"times":xx,"start_time":xx,"end_time":xx,"Freq_seq":xx, "time_seq":xx}}
    """

    # 获取子字典中"eigen"的value值
    item = word_dict["eigen"]
    start_time = item["start_time"]
    end_time = item["end_time"]

    # 通过科大讯飞返回的新的开始和结束的时间，获取在librosa返回的时间列表的索引
    indices = [
        index for index, time in enumerate(times_list) if start_time <= time <= end_time
    ]
    Freq_seq = [Freq_list[index] for index in indices]
    time_seq = [times_list[index] for index in indices]

    item["Freq_seq"] = Freq_seq
    item["time_seq"] = time_seq
    rs_dict = word_dict

    return rs_dict


def getFreqOnset(word_dict: dict, sr: int) -> dict:
    """给定getWordFreqSeq的返回结果使用CQT色度图并给定word长度进行聚类，得到每个word的切割点时间序列

    当word长度>1时，如果：
        没有获得除0以外的切割点，返回时间序列为[0]，代表这个word长度大于1但识别不到切割点（普遍因为word同调）
        获得除0以外的切割点，返回时间序列为[a,b]，将0去掉，a,b为非0的切割点时间
    当word长度=1时，
        返回时间序列为空，代表这个word长度=1，不需要切割点
    将得到的切割时间点序列作为seg_time_list键值添加到输入的字典中。

    参数：
        word_dict(dict):
            getWordFreqSeq的返回结果
        sr(int):
            seg_seq信号序列的采样率

    返回：
        一个字典，结构如下：
            word：词
            eigen：字典，结构如下
                seg_seq：该词对应的ndaaray类型信号序列
                times：歌词持续时间
                start_time
                end_time
                word_start_time
                end_start_time
                Freq_seq：该word的基频f0序列
                time_list：该word的基频f0序列的时间序列
                seg_time_list：本函数获得的长度为word字数的切割时间列表，如果word长度为1，则列表为空。

    """
    eigen = word_dict["eigen"]
    word_len = len(word_dict["word"])
    chroma = librosa.feature.chroma_cqt(y=eigen["seg_seq"], sr=sr)
    bounds = librosa.segment.agglomerative(chroma, word_len)
    bound_times = librosa.frames_to_time(bounds, sr=sr)
    if word_len > 1:
        if len(bound_times) > 1:
            bound_times = np.delete(bound_times, 0).tolist()
        else:
            bound_times = [0]
    elif word_len == 1:
        bound_times = []
    word_dict["eigen"]["seg_time_list"] = bound_times

    return word_dict
