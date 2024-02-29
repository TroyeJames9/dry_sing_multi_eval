# -*- coding: utf-8 -*-

"""pass

pass

"""

from setting import *
import json
import pandas as pd
import numpy as np
import librosa


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


def getPerWordFeat(
    eigen_dict: dict, freq_list: list, times_list: list, crop_percent: float = 0.2
) -> dict:
    """根据adjustWordTime和calAudioFreq的结果来计算每个字的基频f0。

    参数：
        eigen_dict(dict)：
            adjustWordTime的结果
        freq_list(list)：
            calAudioFreq的结果
        times_list(list)：
            calAudioFreq的结果
        crop_percent(float)：
            每个字的基频序列的裁剪比例，默认为0.2

    返回：
        rs_dict(dict)，结构如下：
            eigen_list(list[dict])
                word(str)
                eigen(dict)
                    start_time(float)
                    end_time(float)
                    times(float)
                    freq(float)
    """
    eigen_list = eigen_dict["eigen_list"]
    for i in range(len(eigen_list)):
        item = eigen_list[i]["eigen"]
        times = item["end_time"] - item["start_time"]
        if times > 0.1:
            seg_start_time = item["start_time"] + times * crop_percent
            seg_end_time = item["end_time"] - times * crop_percent

        indices = [
            index
            for index, time in enumerate(times_list)
            if seg_start_time <= time <= seg_end_time
        ]
        freq_seq = [
            freq_list[index] for index in indices if not np.isnan(freq_list[index])
        ]
        item["freq"] = round(np.median(freq_seq), 3)
        item["times"] = round(times, 4)

    return eigen_dict
