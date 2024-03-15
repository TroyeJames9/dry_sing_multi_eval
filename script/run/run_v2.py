# -*- coding: utf-8 -*-

"""
音频处理与音乐评分模块

本模块包含处理音频数据、提取音频特征、计算乐谱特征以及通过动态时间规整（DTW）算法评分的功能。
主要功能包括：
- 批量运行ASR识别处理音频数据
- 批量提取歌曲的音频特征信息
- 从JSON文件中提取对应乐谱特征信息
- 计算音频与乐谱之间的频率和节奏维度的DTW距离，存储于csv中，用于后续

作者: TroyeJmaes9
创建日期: 2024/3/15
修改日期: 2024/3/15
版本: v0.1.2
"""

from setting import *
from util import *
from preprocess.prep_extract import *
from preprocess.audio_eigen_new import *
from preprocess.funasr_go import *
from preprocess.prep_notation import *
from score.audio_score import *

from functools import partial
import numpy as np
import librosa
import copy


def batch_funasr_run(
    input_audio_dataset: str = None,
    input_audio_name: str = None,
    scp_name: str = None,
    input_mode: str = "file",
):
    """详细说明见funasrRun文档字符串"""
    rs_dict = funasrRun(
        input_audio_dataset=input_audio_dataset,
        input_audio_name=input_audio_name,
        scp_name=scp_name,
        input_mode=input_mode,
    )
    rs_dict_list = rs_dict["scp_rs"]

    return rs_dict_list


def getSongFeat(
    rs_dict: dict = None,
    input_audio_dir=UPLOAD_FILE_DIR,
    input_audio_dataset: str = "qilai",
    input_audio_name: str = None,
):
    """
    获取单首歌曲的音频特征信息,颗粒度为字，特征维度暂时包括 字、音长、基频。

    此函数主要负责从指定音频文件中提取音频频率特征，并结合ASR识别结果计算出按词语粒度的音频特征集合。
    由于音频预处理模块存在问题（TODO: 待修复），目前暂时直接读取音频文件进行特征提取。

    参数：
    - rs_dict (dict, 可选): 包含ASR识别结果的字典，键一般为音频文件名前缀，值为ASR识别文本信息。
    - input_audio_dir (str): 音频文件目录，默认指向UPLOAD_FILE_DIR。
    - input_audio_dataset (str): 音频数据集子目录名称，默认为"qilai"。
    - input_audio_name (str, 可选): 指定要处理的音频文件名，若未提供则从rs_dict中获取。

    返回：
    - pwf_dict (dict): 包含单首歌曲音频特征信息的字典，键为音频文件名，值为按照词语粒度计算的音频特征列表。

    """
    pwf_dict = {}  # 初始化存储音频特征的字典

    # 从ASR识别结果中获取词汇信息
    eigen_dict = getWordInfoList(funasr_dict=rs_dict)

    # TODO:临时解决音频预处理问题，直接从指定路径加载音频
    if input_audio_name is None:
        audio_name = rs_dict["key"] + ".wav"  # 若未提供音频文件名，则从rs_dict中获取
    else:
        audio_name = input_audio_name

    # 加载音频文件
    y, sr = librosa.load(input_audio_dir / input_audio_dataset / audio_name)

    # 计算音频的频率和时间信息
    freq_list, times_list = calAudioFreq(reduced_noise=y, sr=int(sr))

    # 计算按词语粒度的音频特征，并存入pwf_dict
    pwf_dict[audio_name] = getPerWordFeat(
        eigen_dict=eigen_dict, freq_list=freq_list, times_list=times_list
    )

    return pwf_dict


def getSheetMusicFeatDict(json_name: str = "guoge"):
    """
    提取乐谱特征字典

    该函数用于从指定的JSON文件中提取乐谱特征信息，并根据不同音调进行处理，形成一个包含不同音调下乐谱特征的字典。

    参数：
    - json_name (str, 默认值="guoge"): 指定要处理的JSON文件名，该文件应包含乐谱信息。

    返回：
    - notation_feat_dict (dict): 一个字典，键为不同的音调（包括原音调及其降半音版本），值为对应的乐谱特征字典。

    """
    key_sig_list = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

    notation_feat_dict = {}  # 初始化乐谱特征字典

    # 遍历所有音调
    for i in range(len(key_sig_list)):
        eigen_dict = extractJson(json_name=json_name)
        eigen_dict_t = calNoteTime(eigen_dict)
        eigen_dict_rs = calNoteFreq(eigen_dict_t, note_sig=key_sig_list[i])
        eigen_dict_rs_copy = copy.deepcopy(eigen_dict_rs)

        # 将原始处理结果添加到notation_feat_dict中，键为当前音调
        notation_feat_dict[key_sig_list[i]] = eigen_dict_rs

        # 创建新键（当前音调降八度）
        new_key_name = key_sig_list[i] + "/2"

        # 遍历特征字典，将音符频率信息除以2（降八度）
        for item in eigen_dict_rs_copy["eigen_list"]:
            item["eigen"]["note"] = [x / 2 for x in item["eigen"]["note"]]

        # 将处理过的特征字典添加至notation_feat_dict中，键为新的音调名称（降八度的调号）
        notation_feat_dict[new_key_name] = eigen_dict_rs_copy

    return notation_feat_dict


def calDtwFreqAndTempo(notation_feat_dict: dict, batch_pwf_dict: dict):
    """
    计算音频与简谱的频率维度与节奏维度的DTW距离，并将结果整理成列表，作为写入CSV的准备数据

    该函数遍历batch_pwf_dict中的每一首歌曲，针对每首歌曲提取其频率和时间特征，并与notation_feat_dict中的乐谱特征进行比较，
    通过计算DTW距离得出每首歌曲在各个音调下的音准和节拍节奏匹配度，最后将这些结果整合为一个字典列表返回。

    参数：
    - notation_feat_dict (dict): 包含不同调号下乐谱特征信息的字典。
    - batch_pwf_dict (dict): 包含多首歌曲按词语粒度的音频特征信息的字典。

    返回：
    - dtw_rs_list (list of dict): 包含每首歌曲在不同音调下，依据音准（频率）和节拍节奏计算的DTW距离结果的字典列表。

    注：该函数内包含一段临时代码，用于演示如何将结果批量写入CSV文件。
    """
    dtw_rs_dict = {}  # 初始化DTW距离结果字典
    dtw_rs_list = []  # 初始化存储最终结果的列表

    # 遍历batch_pwf_dict中的每首歌曲
    for pwf_dict_init in batch_pwf_dict:
        pwd_key = next(iter(pwf_dict_init.keys()))  # 获取歌曲文件名
        pwf_dict = pwf_dict_init[pwd_key]  # 获取歌曲特征字典

        # 提取歌曲的频率特征列表和时间特征列表
        freq_list = [item["eigen"]["freq"] for item in pwf_dict["eigen_list"]]
        times_list = [item["eigen"]["times"] for item in pwf_dict["eigen_list"]]

        dtw_rs_dict[pwd_key] = {}  # 初始化存储该歌曲DTW距离结果的子字典

        # 遍历notation_feat_dict中的每一个调号对应的特征字典
        for nfd_key in notation_feat_dict.keys():
            # 提取当前调号调号下的频率特征列表和音长特征列表
            orignal_freq_list = [
                np.average(item["eigen"]["note"], weights=item["eigen"]["time"])
                for item in notation_feat_dict[nfd_key]["eigen_list"]
            ]
            orignal_times_list = [
                np.sum(item["eigen"]["time"])
                for item in notation_feat_dict[nfd_key]["eigen_list"]
            ]

            # 计算并存储该歌曲在当前调号下的频率和时间特征与乐谱特征的DTW距离
            dtw_rs_dict[pwd_key][nfd_key] = {}
            dtw_rs_dict[pwd_key][nfd_key]["freq_dist"] = useDtw(
                freq_list, orignal_freq_list
            )
            dtw_rs_dict[pwd_key][nfd_key]["tempo_dist"] = useDtw(
                times_list, orignal_times_list
            )

        # 找出该歌曲DTW频率距离最小的调号及相关信息
        min_dtw_tuple = min(
            dtw_rs_dict[pwd_key].items(), key=lambda x: x[1]["freq_dist"]
        )

        # 将每首歌曲在不同调号下的最小DTW距离结果整理为字典，并添加至dtw_rs_list
        for score_field in min_dtw_tuple[1].keys():
            rs_dict = {}
            rs_dict["wav文件名"] = pwd_key
            if "freq" in score_field:
                rs_dict["评分维度"] = "音准"
            elif "tempo" in score_field:
                rs_dict["评分维度"] = "节拍节奏"
            rs_dict["dtw特征值"] = min_dtw_tuple[1][score_field]

            dtw_rs_list.append(rs_dict.copy())

    # ↓ 临时代码，演示批量写入CSV文件
    writeCsv(dtw_rs_list, RAW_DATA_DIR, RESULT_CSV)
    # ↑ 临时代码，演示批量写入CSV文件

    return dtw_rs_list


# TODO
def calDtwFreqAndTempo_V2():
    """
    考虑半音之间的等比数列关系，考虑计算相邻歌词的频率比例作为一个序列来计算DTW
    局限性：只衡量了音准水平，没有衡量音高稳定性
    详见幕布笔记https://mubu.com/app/edit/home/7k-eZzNDgw0#o-72giuusrjB
    """


def main(input_audio_dataset="guoge", scp_name="guoge", input_mode="scp"):
    """
    主函数：用于执行整个音频处理+绝对度量流程，主要包括音频采样、生成SCP文件、ASR批量识别、提取音频特征、提取乐谱特征以及计算DTW，
    目前计算的维度包括音准与节奏节拍


    参数：
    - input_audio_dataset (str, 默认="guoge"): 输入音频数据集的名称。
    - scp_name (str, 默认="guoge"): 生成SCP文件的名称，用于ASR识别。
    - input_mode (str, 默认="scp"): 指定输入模式，默认使用SCP文件方式。

    功能流程：
    1. 通过extractAllAudio函数从指定的input_audio_dataset中提取所有音频样本，并生成对应的采样字典。
    2. 根据采样字典生成用于ASR识别的SCP文件。
    3. 使用指定的音频数据集、SCP文件名以及输入模式调用batch_funasr_run函数，批量进行ASR识别，返回识别结果字典列表rs_dict_list。
    4. 定义一个偏函数getSongFeat_new，将input_audio_dataset作为固定参数传递给getSongFeat函数。
    5. 利用multipuleProcess函数并行处理getSongFeat_new函数，将rs_dict_list作为输入，从而批量提取音频特征，得到song_feat_list。
    6. 调用getSheetMusicFeatDict函数，提取乐谱特征并返回notation_feat_dict。
    7. 计算notation_feat_dict与song_feat_list之间的DTW频率与节奏距离，并打印结果。

    返回：
    无，该函数主要通过执行一系列子任务完成整个音乐处理流程，最终计算并打印DTW相关结果。
    """
    sampling_dict = extractAllAudio(input_audio_dataset=input_audio_dataset)
    getScpFile(sampling_dict)
    rs_dict_list = batch_funasr_run(
        input_audio_dataset=input_audio_dataset,
        scp_name=scp_name,
        input_mode=input_mode,
    )
    getSongFeat_new = partial(getSongFeat, input_audio_dataset=input_audio_dataset)
    song_feat_list = multipuleProcess(getSongFeat_new, rs_dict_list)
    notation_feat_dict = getSheetMusicFeatDict()
    calDtwFreqAndTempo(notation_feat_dict, song_feat_list)


if __name__ == "__main__":
    main("qilai", "qilai")
