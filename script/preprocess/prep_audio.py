"""音频文件的预处理，包括重采样、转为单声道、降噪。

xfrVocalTract方法使用librosa库对音乐重采样为统一的16000并转为单声道的音频，noiseReduce方法使用noisereduce库对音乐进行降噪。

经典的使用案例：

y_resampled, target_sr = xfrVocalTract(dataset_name="qilai", audio_name="qilai_1.mp3")
reduced_noise = noiseReduce(y=y_resampled, sr=target_sr)
"""

# -*- coding: utf-8 -*-
from setting import *
import noisereduce as nr
import librosa
import soundfile as sf
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


# 音频数据由于设备不同，采样率也会不同，为方便研究，需统一采样率；
# 单声道音频比处理立体声音频更简单，兼容性更好，占用更多的存储空间和计算资源更低
def xfrVocalTract(
    audio_dir: Path = UPLOAD_FILE_DIR,
    dataset_name: str = None,
    audio_name: str = None,
    target_sr: int = 16000,
) -> tuple:
    """按照target_sr进行重采样后，将声道数转化为指定数（一般项目需求为单声道）

    假设某一首歌的路径为 /Users/lijianxin/speech_recognition/audio/mp3/xxx.mp3

    参数：
        audio_dir：
            默认根目录为setting文件中的UPLOAD_FILE_DIR，eg：audio文件的路径。
        dataset_name：
            音频文件除去根目录和音频名之间的部分，eg：mp3。
        audio_name:
            音频名,eg:xxx.mp3。
        target_sr：
            目标的采样率，16000为常用的采用率。
        vt_num:
            需要设置的声道数。

    返回：
        1个元组，单声道音频文件的时域信号（一维的NumPy数组）y_resampled 和目标采样率target_sr。
    """

    if dataset_name is None:
        raise ValueError("音频文件夹不能为空")

    if audio_name is None:
        raise ValueError("文件夹下的音频文件名不能为空")

    audio_path = os.path.join(audio_dir, dataset_name, audio_name)  # 使用 / 拼接路径

    # 读取音频文件
    y, sr = librosa.load(audio_path, sr=None)

    # 重采样
    y_resampled = librosa.resample(y, orig_sr=sr, target_sr=target_sr)

    # 将音频信号转换为单声道
    y_resampled = librosa.to_mono(y_resampled)

    return y_resampled, target_sr


def noiseReduce(
    y: np.ndarray = None,
    sr: int = None,
    prop_decrease: float = 0.8,
    stationary: bool = False,
) -> np.ndarray:
    """将重采样后的数据y_resampled进行降噪，消除非人声噪音.

     noiseReduce库参数：https://github.com/timsainb/noisereduce

     参数 ：
         y:
             加载的音频文件的时域信号，是一个一维的NumPy数组。
         sr:
             音频的采样率。
         thresh_n_mult_nonstationary:
             降噪的幅度，只能用于动态降噪中，数值越大，降噪的幅度越大。
         prop_decrease:
            降噪的比例，数字1表示降噪百分百。
         stationary:
             布尔值，True表示平稳降噪 ，False表示非平稳降噪。

    返回：
        降噪后的一维的NumPy数组的音频文件的时域信号。
    """
    reduced_noise = nr.reduce_noise(
        y=y,
        sr=sr,
        prop_decrease=prop_decrease,
        stationary=stationary,
    )

    return reduced_noise
