"""音频文件的预处理，包括重采样、转为单声道、降噪。

xfrVocalTract方法使用librosa库对音乐重采样为统一的16000并转为单声道的音频，noiseReduce方法使用noisereduce库对音乐进行降噪。

经典的使用案例：

y_resampled, target_sr = xfrVocalTract(dataset_name="mp3", audio_name="广东番禺中学附属学校_万可之.mp3")
reduced_noise = noiseReduce(y=y_resampled, sr=target_sr, thresh_n_mult_nonstationary=3)
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
def xfrVocalTract(audio_dir: Path = UPLOAD_FILE_DIR, dataset_name: str = None, audio_name: str = None,
                  target_sr: Number = 16000,
                  vt_num: Number = 1) -> int:
    """按照target_sr进行重采样后，将声道数转化为指定数（一般项目需求为单声道）
    pass






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

    # 转换为单声道
    if vt_num == 1 and len(y_resampled.shape) > 1:
        y_resampled = np.mean(y_resampled, axis=0)

    return y_resampled, target_sr


def noiseReduce(y=None, sr=None, thresh_n_mult_nonstationary=2, y_noise=None, stationary=None):
    reduced_noise = nr.reduce_noise(y=y,
                                    sr=sr,
                                    thresh_n_mult_nonstationary=thresh_n_mult_nonstationary,
                                    y_noise=y_noise,
                                    stationary=stationary)

    return reduced_noise


y_resampled, target_sr = xfrVocalTract(dataset_name="mp3", audio_name="广东番禺中学附属学校_万可之.mp3")
# audio_file = "/Users/lijianxin/speech_recognition/audio/mp3/广东番禺中学附属学校_万可之.mp3"
# y, sr = librosa.load(audio_file, sr=None)

a = noiseReduce(y=y_resampled, sr=target_sr, thresh_n_mult_nonstationary=3)
print(a)

# fig, ax = plt.subplots(figsize=(20, 3))
# ax.plot(y_resampled)
# ax.plot(y, alpha=1)
# plt.show()
