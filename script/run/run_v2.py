# -*- coding: utf-8 -*-

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
    rs_dict = funasrRun(input_audio_dataset=input_audio_dataset, input_audio_name=input_audio_name, scp_name=scp_name,
                        input_mode=input_mode)
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

        dtw_rs_dict[pwd_key] = {}

        # 提取notation_feat_dict 字典里的所有times和note，分别按顺序得到orignal_freq_list和orignal_times_list
        for nfd_key in notation_feat_dict.keys():
            orignal_freq_list = [
                np.average(item["eigen"]["note"], weights=item["eigen"]["time"])
                for item in notation_feat_dict[nfd_key]["eigen_list"]
            ]
            orignal_times_list = [
                np.sum(item["eigen"]["time"])
                for item in notation_feat_dict[nfd_key]["eigen_list"]
            ]

            dtw_rs_dict[pwd_key][nfd_key] = {}
            dtw_rs_dict[pwd_key][nfd_key]["freq_dist"] = useDtw(
                freq_list, orignal_freq_list
            )
            dtw_rs_dict[pwd_key][nfd_key]["tempo_dist"] = useDtw(
                times_list, orignal_times_list
            )

        min_dtw_tuple = min(
            dtw_rs_dict[pwd_key].items(), key=lambda x: x[1]["freq_dist"]
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
    writeCsv(dtw_rs_list, RAW_DATA_DIR, RESULT_CSV)
    """↑ temp,演示批量写入EXCEL使用"""

    return dtw_rs_list


# TODO
def calDtwFreqAndTempo_V2():
    """
    考虑半音之间的等比数列关系，考虑计算相邻歌词的频率比例作为一个序列来计算DTW
    局限性：只衡量了音准水平，没有衡量音高稳定性
    详见幕布笔记https://mubu.com/app/edit/home/7k-eZzNDgw0#o-72giuusrjB
    """


def main(
    input_audio_dataset="guoge",
    scp_name="guoge",
    input_mode="scp",
):
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
    print(calDtwFreqAndTempo(notation_feat_dict, song_feat_list))


if __name__ == "__main__":
    main("qilai", "qilai")
