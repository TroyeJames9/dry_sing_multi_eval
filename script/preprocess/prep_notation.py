# -*- coding: utf-8 -*-

"""模块功能描述

简谱特征提取模块，通过定义extractJson、calNoteTime、calNoteFreq方法，分别将JSON简谱文件识别并提取为字典格式后，通过曲子的BPM和拍号
计算出每个歌词的音长，最后算出每个切割后的词所对应的频率。

简谱信息json文件的数据结构参考本项目文档 ”简记简谱分析模块“

经典的使用示例：

data = extractJson(json_name="guoge")
eigen_dict_t = calNoteTime(eigen_dict = data)
eigen_dict_rs = calNoteFreq(eigen_dict_t, note_sig='G')
"""

from setting import *
import json
import pandas as pd


def extractJson(json_dir: Path = EIGEN_DIR, json_name: str = None):
    """
    读取指定目录下的JSON文件，并将其内容转换为字典格式。

    该函数通过指定的路径和文件名加载JSON文件，并将文件内容转换为Python字典。

    参数：
    - json_dir: Path，JSON文件所在的根目录，例如：EIGEN_DIR = ROOT / "eigen_json"
    - json_name: str，JSON文件的名称（不带后缀.json），如果提供了后缀，它将被自动添加

    返回：
    - eigen_dict: dict，结构如下：{"bpm": int,
                                 "key_signature": 'G',
                                 "time_signature":  [int, int],
                                 "eigen_list": ["word": str, "eigen":{note: list, time: list}]
                                }
    """

    # 如果提供的json_name没有后缀，则添加.json后缀
    json_name = json_name + ".json" if not json_name.endswith(".json") else json_name

    # 构造JSON文件的完整路径
    json_filename = os.path.join(str(json_dir), json_name)  # 注意：Path对象需要转换为字符串

    # 使用with语句打开文件，这样可以确保文件在使用后会被正确关闭
    # 打开文件时指定编码为gbk，以处理可能的中文或其他非ASCII字符
    with open(json_filename, "r", encoding="gbk") as f:
        # 使用json模块的load方法将文件内容解析为字典
        data = json.load(f)
        eigen_dict = data

    return eigen_dict


def calNoteTime(eigen_dict: dict) -> dict:
    """传入extractJson的输出结果，根据bpm和time_signature来计算所有note对应的音长，单位为秒

    音长的计算公式为：（60÷BPM）×（拍号的分母/4）× 每个词的拍数

    参数：eigen_dict：
        将extractJson读取的JSON文件结果传进来。

    返回：
        eigen_dict_t:
            原始JSON中time键所对应的value值替换为音长
    """
    bpm = eigen_dict["bpm"]  # 存储简谱中的BPM值
    note = eigen_dict["time_signature"][1]

    """遍历文件eigen_dict下的eigen_list键中所嵌套的dict值，将子键值对eigen中将time提取出来，通过公式计算后的音长替换掉原来的时间"""
    eigen_list = eigen_dict["eigen_list"]
    for eigen in eigen_list:
        time = eigen["eigen"]["time"]
        word_duration = [60 / bpm * note / 4 * t for t in time]
        eigen["eigen"]["time"] = word_duration
    eigen_dict_t = eigen_dict

    return eigen_dict_t


def calNoteFreq(
        eigen_dict_t: dict, data_dir: Path = RAW_DATA_DIR, data_name: str = FREQ_CSV, note_sig: str = None
) -> dict:
    """
   根据调号音符频率表以及给定的调号，计算调号对应的简谱里所有音符的频率，并将计算出来的频率值替换掉以前的JSON文件中的note值。

   参数：
   - eigen_dict_t: dict，calNoteTime处理后的JSON文件，其中包含简谱信息。
   - data_dir: Path，调号音符频率表所在目录的绝对路径，默认为RAW_DATA_DIR。
   - data_name: str，调号音符频率表的名称，默认为FREQ_CSV。
   - note_sig: str，调号，乐理中的概念。取值范围为调号频率表的音名1列和音名2列取值范围。

   返回：
   - eigen_dict_rs: dict，将calNoteTime处理后JSON中note键所对应的value值替换为频率。
   """

    csv_filename = os.path.join(str(data_dir), data_name)  # 注意：Path对象需要转换为字符串
    df = pd.read_csv(csv_filename, encoding="gbk")

    # 筛选出与给定调号匹配的音符频率信息
    matched_rows = df[(df["音名1"] == note_sig) | (df["音名2"] == note_sig)]
    eigen_list = eigen_dict_t["eigen_list"]

    # 提取简谱列表中所有音符的名称
    notes = []
    for eigen in eigen_list:
        note = eigen["eigen"]["note"]
        notes.append(note)

    # 遍历音符列表，计算每个音符的频率
    for sublist in notes:
        for i in range(len(sublist)):
            item = sublist[i]
            negative_count = 0  # 用于统计'-'的个数
            positive_count = 0  # 用于统计'+'的个数
            numbers = []  # 用于存储除去符号后的数字

            # 计算音符名称中的'+'和'-'符号数量
            for char in item:
                if char == "-":
                    negative_count += char.count("-")
                elif char == "+":
                    positive_count += char.count("+")

            # 提取音符名称中的数字部分
            number = item.replace("-", "").replace("+", "")
            numbers.append(number)

            # 根据音符名称从频率表查找对应的频率
            matched_freq = matched_rows[matched_rows["唱名"] == number]["频率"].values

            # 如果找到频率，则处理符号对频率的影响,+号相当于升八度，减号相当于降八度
            if len(matched_freq) > 0:
                matched_freq = matched_freq[0]
                if negative_count > 0 and positive_count == 0:
                    matched_freq = matched_freq * 0.5 ** negative_count
                elif positive_count > 0 and negative_count == 0:
                    matched_freq = matched_freq * 2 ** positive_count
            else:
                matched_freq = None

            sublist[i] = matched_freq

    eigen_dict_rs = eigen_dict_t
    return eigen_dict_rs


if __name__ == "__main__":
    data = extractJson(json_name="guoge")
    eigen_dict_t = calNoteTime(eigen_dict=data)
    eigen_dict_rs = calNoteFreq(eigen_dict_t, note_sig='G')
