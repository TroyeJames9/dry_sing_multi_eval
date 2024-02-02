# -*- coding: utf-8 -*-

"""模块功能描述

详细描述

"""

from setting import *
import json
import pandas as pd


def extractJson(json_dir: Path = EIGEN_DIR, json_name: str = None):
    """提取json文件，将其输出为字典格式"""

    json_name = json_name + ".json"
    json_filename = os.path.join(json_dir, json_name)
    with open(json_filename, "r", encoding="gbk") as f:
        data = json.load(f)
    return data


def calNoteTime(eigen_dict: dict):
    """传入extractJson的输出结果，根据bpm和time_signature来计算所有note对应的音长，单位为秒"""
    bpm = eigen_dict["bpm"]
    note = eigen_dict["time_signature"][1]

    eigen_list = eigen_dict["eigen_list"]
    for eigen in eigen_list:
        time = eigen["eigen"]["time"]
        word_duration = [60 / bpm * note / 4 * t for t in time]
        eigen["eigen"]["time"] = word_duration
    eigen_dict_t = eigen_dict

    return eigen_dict_t


def calNoteFreq(eigen_dict_t: dict, data_dir: Path, data_name: str, note_sig: str):
    """传入calNoteTime的输出结果，根据raw_data中的调号音符频率表以及给定的调号，计算调号对应的简谱里所有音符的频率，单位为HZ"""
    # 读取CSV文件
    df = pd.read_csv('调号音符频率表.csv', encoding='gbk')

    with open(eigen_dict_t, 'r', encoding='gbk') as f:
        data = json.load(f)

    key_signature = data['key_signature']
    matched_rows = df[(df['音名1'] == key_signature) | (df['音名2'] == key_signature)]
    matched_rows




    pass
