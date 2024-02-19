# -*- coding: utf-8 -*-

"""模块功能描述

简谱特征提取模块，通过定义extractJson、calNoteTime、calNoteFreq方法，分别将JSON简谱文件识别并提取为字典格式后，通过曲子的BPM和拍号
计算出每个歌词的音长，最后算出每个切割后的词所对应的频率。

经典的使用示例：

data = extractJson()
eigen_dict_t = calNoteTime(eigen_dict = data)
eigen_dict_rs = calNoteFreq()
"""

from setting import *
import json
import pandas as pd


def extractJson(json_dir: Path = EIGEN_DIR, json_name: str = None):
    """提取json文件，将其输出为字典格式。

    通过指定的路径，将JSON文件的内容识别出来，并转为dict格式输出。

    参数：
        json_dir：
            根目录，eg：EIGEN_DIR = ROOT / "eigen_json"。
        json_name：
            去掉尾缀后的文件名，eg：self.json_name = "中华人民共和国国歌测试"。

    返回：
        eigen_dict为从JSON文件中提出的结果。

    """

    json_name = json_name + ".json"
    json_filename = os.path.join(json_dir, json_name)
    '''使用with方法，文件加载后赋值给data后会自动关闭，无需写代码手动关闭'''
    with open(json_filename, "r", encoding="gbk") as f:
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
    eigen_dict_t: dict, data_dir: Path, data_name: str, note_sig: str
) -> dict:
    """传入calNoteTime的输出结果,计算每个词的频率。

    根据raw_data中的调号音符频率表以及给定的调号，计算调号对应的简谱里所有音符的频率，单位为HZ，计算出简谱中eigen_list所有word对应的频率值，
    并将计算出来的频率值替换掉以前的JSON文件中的note值。

    参数：
        eigen_dict_t：
            calNoteTime处理后的JSON文件。
        data_dir：
            调号音符频率表所在目录的绝对路径,默认为RAW_DATA_DIR。
        data_name：
            调号音符频率表的名称，默认为FREQ_CSV。
        note_sig：
            调号，乐理中的概念。取值范围为调号频率表的音名1 列和音名2列取值范围。

    返回：
        eigen_dict_rs:
            将calNoteTime处理后JSON中note键所对应的value值替换为频率

    """

    csv_filename = os.path.join(data_dir, data_name)  # 拼接csv文件所在的路径
    df = pd.read_csv(csv_filename, encoding="gbk")  # 读取音符频率表
    # matched_rows为子表，根据传入的调号note_sig找出相应音名的子表
    matched_rows = df[(df["音名1"] == note_sig) | (df["音名2"] == note_sig)]

    # 在传进的JSON文件中，定位到多层键值对下的eigen_list，并将对应的键值对赋值给eigen_list
    eigen_list = eigen_dict_t["eigen_list"]

    notes = []  # 用来存放JSON文件中的note键对应的value值
    """遍历eigen_list中所有的eigen下的子键值对，将note所对应的值存储到notes中，eg：notes=[['-5'], ['1'], ['1'], ['1'], ['+1'], ['-1', '--6']]"""
    for eigen in eigen_list:
        note = eigen["eigen"]["note"]
        notes.append(note)

    """第一层for循环进入到所有的子列表中，eg：['-5']，第二层for循环进入到该子列表中的数字，eg：-5，第三层for循环识别统计有多少个'+'，'-'符号"""
    for sublist in notes:
        for i in range(len(sublist)):
            item = sublist[i]
            negative_count = 0  # 用于统计'-'的个数
            positive_count = 0  # 用于统计'+'的个数
            numbers = []  # 用于存储第三层循环中除去符号后的数字，eg：'-5'——>5

            for char in item:
                if char == "-":
                    negative_count += char.count("-")
                elif char == "+":
                    positive_count += char.count("+")

            number = char.replace("-", "").replace("+", "")
            numbers.append(number)
            # 找出音名所对应的频率值
            matched_freq = matched_rows[matched_rows["唱名"] == number]["频率"].values
            """如果找到的频率值长度大于0，则取出，否则赋值为None"""
            if len(matched_freq) > 0:
                matched_freq = matched_freq[0]
            else:
                matched_freq = None
            """如果第二层循环取出的数字有'+'符号是，表示频率值需变为2的指数倍，eg：'++3'表示为，频率值为4倍（2的平方=4）音名3的频率；
            取出的数字有'-'号表示频率值变为1/2的指数倍；如果没有'+'，'-'符号，则直接取出频率值"""
            if negative_count > 0 and positive_count == 0:
                matched_freq = matched_freq * 0.5**negative_count
            elif positive_count > 0 and negative_count == 0:
                matched_freq = matched_freq * 2**positive_count
            else:
                matched_freq = matched_freq
            """将计算出来的音符的频率值替换掉原JSON文件中的note的值，将替换放在第二层是因为遇到特殊子表['+1', '--6']时，可以不破坏子列表的结构也可以将计算后频率值放回"""
            sublist[i] = matched_freq

    eigen_dict_rs = eigen_dict_t

    return eigen_dict_rs
