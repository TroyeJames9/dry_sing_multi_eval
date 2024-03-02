# -*- coding: utf-8 -*-

from setting import *
from dtw import *
from preprocess.prep_extract import *
from preprocess.audio_eigen_new import *
from preprocess.funasr_go import *
from preprocess.prep_notation import *
from score.audio_score import *
import numpy as np
import librosa
import copy


def getSingleSongFeat(
    input_audio_dir: Path = UPLOAD_FILE_DIR,
    input_audio_dataset: str = "qilai",
    input_audio_name: str = "cst.mp3",
):
    rs_dict = funasr_run(
        input_audio_dataset=input_audio_dataset, input_audio_name=input_audio_name
    )
    eigen_dict = getWordInfoList(funasr_dict=rs_dict)
    y, sr = librosa.load(input_audio_dir / input_audio_dataset / input_audio_name)
    freq_list, times_list = calAudioFreq(reduced_noise=y, sr=sr)
    pwf_dict = getPerWordFeat(
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


def calDtwFreqAndTempo(notation_feat_dict: dict, pwf_dict: dict):
    # 提取pwf_dict 字典里的所有times和freq，分别按顺序得到times_list和freq_list
    freq_list = [item["eigen"]["freq"] for item in pwf_dict["eigen_list"]]
    times_list = [item["eigen"]["times"] for item in pwf_dict["eigen_list"]]
    z_freq_list = z_score_normalization(freq_list)
    z_times_list = z_score_normalization(times_list)

    dtw_rs_dict = {}

    # 提取notation_feat_dict 字典里的所有times和note，分别按顺序得到orignal_freq_list和orignal_times_list
    for key in notation_feat_dict.keys():
        orignal_freq_list = [
            np.average(item["eigen"]["note"], weights=item["eigen"]["time"])
            for item in notation_feat_dict[key]["eigen_list"]
        ]
        z_orignal_freq_list = z_score_normalization(orignal_freq_list)
        freq_dtw_rs = dtw(z_freq_list, z_orignal_freq_list, dist_method="euclidean")

        orignal_times_list = [
            np.sum(item["eigen"]["time"])
            for item in notation_feat_dict[key]["eigen_list"]
        ]
        z_orignal_times_list = z_score_normalization(orignal_times_list)
        tempo_dtw_rs = dtw(z_times_list, z_orignal_times_list, dist_method="euclidean")

        dtw_rs_dict[key] = {}
        # dtw_rs_dict[key]["freq_dist_normalized"] = freq_dtw_rs.normalizedDistance
        # dtw_rs_dict[key]["tempo_dist_normalized"] = tempo_dtw_rs.normalizedDistance
        dtw_rs_dict[key]["freq_dist_normalized"] = freq_dtw_rs.distance
        dtw_rs_dict[key]["tempo_dist_normalized"] = tempo_dtw_rs.distance

    return dtw_rs_dict


# TODO
def calDtwFreqAndTempo_V2():
    """
    考虑半音之间的等比数列关系，考虑计算相邻歌词的频率比例作为一个序列来计算DTW
    局限性：只衡量了音准水平，没有衡量音高稳定性
    详见幕布笔记https://mubu.com/app/edit/home/7k-eZzNDgw0#o-72giuusrjB
    """


if __name__ == "__main__":
    pwf_dict = getSingleSongFeat(input_audio_name="qilai_4.mp3")
    notation_feat_dict = getSheetMusicFeatDict()
    print(calDtwFreqAndTempo(notation_feat_dict, pwf_dict))
