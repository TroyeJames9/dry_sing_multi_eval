# -*- coding: utf-8 -*-

from setting import *
from dtw import *
from preprocess.prep_extract import *
from preprocess.audio_eigen_new import *
from preprocess.funasr_go import *
from preprocess.prep_notation import *
from score.audio_score import *
from functools import partial
import multiprocessing
import concurrent.futures
import numpy as np
import librosa
import copy
import pandas as pd
import csv


def batch_funasr_run(
    input_audio_dataset: str = "qilai",
    input_audio_name: str = None,
    song_name: str = "guoge",
    input_mode: str = "file",
):
    rs_dict = funasr_run(
        input_audio_dataset=input_audio_dataset,
        input_audio_name=input_audio_name,
        song_name=song_name,
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
    pwf_dict = {}
    eigen_dict = getWordInfoList(funasr_dict=rs_dict)

    # temp，因为音频预处理模块出问题了，暂时直接提取
    if input_audio_name is None:
        audio_name = rs_dict["key"] + ".wav"
    else:
        audio_name = input_audio_name
    y, sr = librosa.load(input_audio_dir / input_audio_dataset / audio_name)

    freq_list, times_list = calAudioFreq(reduced_noise=y, sr=sr)
    pwf_dict[audio_name] = getPerWordFeat(
        eigen_dict=eigen_dict, freq_list=freq_list, times_list=times_list
    )

    return pwf_dict


def processGetSongFeat(
    input_audio_dataset: str = "qilai",
    input_audio_name: str = None,
    rs_dict_list: dict = None,
):
    getSongFeat_new = partial(getSongFeat, input_audio_dir=UPLOAD_FILE_DIR, input_audio_dataset=input_audio_dataset, input_audio_name=input_audio_name)
    with concurrent.futures.ProcessPoolExecutor(4) as executor:
        # 使用map方法并发执行函数
        chunksize = 8
        result_list = list(
            executor.map(
                getSongFeat_new,
                rs_dict_list,
                chunksize=chunksize
            )
        )

    return result_list


def getSheetMusicFeatDict(json_name: str = "guoge"):
    key_sig_list = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

    notation_feat_dict = {}
    for i in range(len(key_sig_list)):
        eigen_dict = extractJson(json_name=json_name)
        eigen_dict_t = calNoteTime(eigen_dict)
        eigen_dict_rs = calNoteFreq(eigen_dict_t, note_sig=key_sig_list[i])

        # 进行深拷贝
        eigen_dict_rs_copy = copy.deepcopy(eigen_dict_rs)

        notation_feat_dict[key_sig_list[i]] = eigen_dict_rs

        new_key_name = key_sig_list[i] + "/2"
        # 遍历每个 eigen 字典，将 note 键对应的值除以 2
        for item in eigen_dict_rs_copy["eigen_list"]:
            item["eigen"]["note"] = [x / 2 for x in item["eigen"]["note"]]
        notation_feat_dict[new_key_name] = eigen_dict_rs_copy

    return notation_feat_dict


def calDtwFreqAndTempo(notation_feat_dict: dict, batch_pwf_dict: dict):
    dtw_rs_dict = {}
    dtw_rs_list = []

    for pwf_dict_init in batch_pwf_dict:
        pwd_key = next(iter(pwf_dict_init.keys()))
        pwf_dict = pwf_dict_init[pwd_key]
        # 提取pwf_dict 字典里的所有times和freq，分别按顺序得到times_list和freq_list
        freq_list = [item["eigen"]["freq"] for item in pwf_dict["eigen_list"]]
        times_list = [item["eigen"]["times"] for item in pwf_dict["eigen_list"]]
        z_freq_list = z_score_normalization(freq_list)
        z_times_list = z_score_normalization(times_list)

        dtw_rs_dict[pwd_key] = {}

        # 提取notation_feat_dict 字典里的所有times和note，分别按顺序得到orignal_freq_list和orignal_times_list
        for nfd_key in notation_feat_dict.keys():
            orignal_freq_list = [
                np.average(item["eigen"]["note"], weights=item["eigen"]["time"])
                for item in notation_feat_dict[nfd_key]["eigen_list"]
            ]
            z_orignal_freq_list = z_score_normalization(orignal_freq_list)
            freq_dtw_rs = dtw(z_freq_list, z_orignal_freq_list, dist_method="euclidean")

            orignal_times_list = [
                np.sum(item["eigen"]["time"])
                for item in notation_feat_dict[nfd_key]["eigen_list"]
            ]
            z_orignal_times_list = z_score_normalization(orignal_times_list)
            tempo_dtw_rs = dtw(
                z_times_list, z_orignal_times_list, dist_method="euclidean"
            )

            dtw_rs_dict[pwd_key][nfd_key] = {}
            dtw_rs_dict[pwd_key][nfd_key][
                "freq_dist_normalized"
            ] = freq_dtw_rs.normalizedDistance
            dtw_rs_dict[pwd_key][nfd_key][
                "tempo_dist_normalized"
            ] = tempo_dtw_rs.normalizedDistance

        min_dtw_tuple = min(
            dtw_rs_dict[pwd_key].items(), key=lambda x: x[1]["freq_dist_normalized"]
        )

        # rs_dict[pwd_key]["key_sig"] = min_dtw_tuple[0]
        # rs_dict[pwd_key]["score"] = min_dtw_tuple[1]

        for score_field in min_dtw_tuple[1].keys():
            rs_dict = {}
            rs_dict["wav文件名"] = pwd_key
            if "freq" in score_field:
                rs_dict["评分维度"] = "音准"
            elif "tempo" in score_field:
                rs_dict["评分维度"] = "节拍节奏"
            rs_dict["dtw特征值"] = min_dtw_tuple[1][score_field]

            dtw_rs_list.append(rs_dict.copy())

    """↓ temp,演示批量写入csv使用"""
    csv_file_path = RAW_DATA_DIR / RESULT_CSV
    if not os.path.isfile(csv_file_path):
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=list(rs_dict.keys()))
            writer.writeheader()
            writer.writerows(dtw_rs_list)
    else:
        # 如果文件已存在，则以追加模式打开
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=list(rs_dict.keys()))
            writer.writerows(dtw_rs_list)

    print("CSV文件已创建或更新：", csv_file_path)
    """↑ temp,演示批量写入EXCEL使用"""

    return rs_dict


# TODO
def calDtwFreqAndTempo_V2():
    """
    考虑半音之间的等比数列关系，考虑计算相邻歌词的频率比例作为一个序列来计算DTW
    局限性：只衡量了音准水平，没有衡量音高稳定性
    详见幕布笔记https://mubu.com/app/edit/home/7k-eZzNDgw0#o-72giuusrjB
    """


if __name__ == "__main__":
    # rs_dict = getSongFeat(input_audio_name="cst.wav")
    rs_dict_list = batch_funasr_run(input_audio_dataset="guoge", song_name="guoge", input_mode="scp")
    song_feat_list = processGetSongFeat(input_audio_dataset="guoge", rs_dict_list=rs_dict_list)
    notation_feat_dict = getSheetMusicFeatDict()
    print(calDtwFreqAndTempo(notation_feat_dict, song_feat_list))
