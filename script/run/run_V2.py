# -*- coding: utf-8 -*-

from setting import *
from preprocess.audio_eigen_new import *
from preprocess.funasr_go import *
from preprocess.prep_notation import *
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


def getSheetMusicFeatDict(json_name: str = "国歌"):
    key_sig_list = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

    notation_feat_dict = {}
    for i in range(len(key_sig_list)):
        eigen_dict = extractJson(json_name=json_name)
        eigen_dict_t = calNoteTime(eigen_dict)
        eigen_dict_rs = calNoteFreq(eigen_dict_t, note_sig=key_sig_list[i])

        # 进行深拷贝
        eigen_dict_rs_copy = copy.deepcopy(eigen_dict_rs)

        notation_feat_dict[key_sig_list[i]] = eigen_dict_rs_copy

        new_key_name = key_sig_list[i] + "/2"
        # 遍历每个 eigen 字典，将 note 键对应的值除以 2
        for item in eigen_dict_rs_copy['eigen_list']:
            item['eigen']['note'] = [x / 2 for x in item['eigen']['note']]
        notation_feat_dict[new_key_name] = eigen_dict_rs_copy

    return notation_feat_dict


if __name__ == "__main__":
    # print(getSingleSongFeat())
    print(getSheetMusicFeatDict())
