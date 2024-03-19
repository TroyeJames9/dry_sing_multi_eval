# -*- coding: utf-8 -*-

"""本模块主要从文件歌曲表提取曲目对应的文件列表作为数据集，或者直接从数据集目录提取所有文件生成scp文件作为数据集。

经典的使用案例：
    1) 生成的scp文件可用于funASR识别
    sampling_dict = extractAllAudio(input_audio_dataset="qilai")
    getScpFile(sampling_dict)

    2) 结果可用于从funASR识别结果的json文件提取对应的音频信息
    sample_dict = audioSampling(song_names=["guoge", "molihua"], max_samples=1000)
"""

import pandas as pd
from pathlib import Path
import logging
from itertools import groupby
import random
from setting import *

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format="%(message)s")


def audioSampling(
    csv_dir=RAW_DATA_DIR, csv_name=SONGNAME_CSV, song_names: list = None, max_samples=5
):
    """
    从CSV文件中提取指定曲目、指定数量的数据行，并将其保存为字典的形式。
    键名为曲目名称，键值为曲目对应的指定数量的文件名列表（不带后缀）。
    如果指定数量大于曲目对应的行数，则对应列表存储曲目所有的文件名。

    参数：
    - csv_dir: Path，包含音频数据的CSV文件所在目录的绝对路径，默认为RAW_DATA_DIR
    - csv_name: str，包含音频曲目信息的CSV文件名称，默认为SONGNAME_CSV，
                CSV文件应只包含"文件名"和"曲目"两个字段
    - song_names: list，用于匹配曲目名称的正则表达式列表
    - max_samples: int，每个曲目最大抽取的数据行数，默认为5

    返回：
    - sampled_tracks: dict，结构为{<曲目名称1>: [文件名1, 文件名2, ...],
                                     <曲目名称2>: [文件名1, 文件名2, ...]}
    """
    csv_file_path = csv_dir / csv_name
    df = pd.read_csv(csv_file_path, encoding="gbk", engine="python")

    # 构造一个正则表达式，用于匹配列表中的所有曲目名称
    # 使用case=False忽略大小写，na=False处理缺失值
    combined_regex = "|".join(song_names)
    selected_rows = df[df["曲目"].str.contains(combined_regex, case=False, na=False)]

    # 将筛选后的数据帧转换为记录列表
    selected_rows = selected_rows.to_dict("records")

    # 对记录列表进行排序，并按曲目名称分组
    grouped_music = groupby(
        sorted(selected_rows, key=lambda x: x["曲目"]), lambda x: x["曲目"]
    )

    # 初始化一个空字典，用于存储按曲目分组的文件名列表
    grouped_by_song = {}

    # 遍历每个曲目组，并提取文件名放入对应曲目字典中
    for track, group in grouped_music:
        file_names = [item["文件名"] for item in group]
        grouped_by_song[track] = file_names

    # 对每个曲目的文件列表进行随机抽样，数量不足时取全部
    sampled_tracks = {
        track: random.sample(files, min(len(files), max_samples))
        for track, files in grouped_by_song.items()
    }
    print("audioSampling: The sampling of the specified audio data set is completed, the extracted tracks include '", song_names, "',the sample size is", max_samples)

    return sampled_tracks


def extractAllAudio(input_audio_dataset: str, input_dir: Path = UPLOAD_FILE_DIR):
    """
    提取指定数据集目录下的所有音频文件路径，并将它们存储在一个字典中。

    参数:
    - input_audio_dataset: str，要提取文件的数据集目录名称
    - input_dir: Path，数据集的父目录，默认为UPLOAD_FILE_DIR（setting.py定义）

    返回:
    - sampling_dict: dict，结构为{<数据集名称>: [音频文件路径1, 音频文件路径2, ...]}
    """

    # 初始化一个空字典，用于存储文件路径
    sampling_dict = {}

    folder_path = input_dir / input_audio_dataset

    # 使用列表推导式遍历目录中的所有文件，并获取它们的绝对路径
    sampling_dict[input_audio_dataset] = [
        os.path.abspath(os.path.join(folder_path, filename))  # 获取每个文件的绝对路径
        for filename in os.listdir(folder_path)  # 遍历目录中的所有文件名
    ]
    print("extractAllAudio: Extract all audio file paths from the dataset", input_audio_dataset)
    # 返回包含所有音频文件路径的字典
    return sampling_dict


def getScpFile(sampling_dict: dict, scp_dir: Path = SCP_DATA_DIR):
    """
    将形同{song_name: [file_path1, file_path2, ...]}的字典转化成scp文件存储。

    scp文件格式见
    https://eleanorchodroff.com/tutorial/kaldi/training-acoustic-models.html#wav.scp
    生成的scp文件名为(song_name + ".scp")。

    参数:
    - sampling_dict: 字典，形如{song_name: [file_path1, file_path2, ...]}
    - scp_dir: scp文件存储路径，默认为SCP_DATA_DIR（在setting.py定义）

    返回:
    - 无返回值，直接写入scp文件
    """
    # 遍历字典中的每个键（数据集名称）
    for song_name in sampling_dict.keys():
        files_list = sampling_dict[song_name]  # 获取对应数据集的文件路径列表
        scp_dict = {}  # 初始化一个新的字典用于scp文件内容

        # 遍历歌曲的文件路径列表
        for file_path in files_list:
            file_name = os.path.basename(file_path)  # 获取文件名
            # 使用正则表达式移除文件扩展名
            file_name = re.sub(r"\..*", "", file_name)
            scp_dict[file_name] = file_path  # 将文件名和路径添加到scp字典

        # 构造scp文件的名称和路径
        scp_name = song_name + ".scp"
        scp_path = scp_dir / scp_name

        # 如果scp文件已存在，则清空文件内容
        if os.path.exists(scp_path):
            open(scp_path, "w").close()

        # 打开scp文件并写入scp字典的内容
        with open(scp_path, "w") as f:
            for key, value in scp_dict.items():
                # 将路径中的反斜杠替换为斜杠，以便兼容不同操作系统
                value = value.replace("\\", "/")
                # 写入scp文件，格式为"key value"
                f.write(f"{key} {value}\n")
    print("getScpFile: Store dataset into ", scp_path)
    # 函数没有返回值，因为结果已经写入到了scp文件中
    # 注：如果需要返回scp_dict，可以添加 return scp_dict


def extractRun():
    sampling_dict = extractAllAudio(input_audio_dataset="qilai")
    getScpFile(sampling_dict)


def test_audioSampling():
    test_1 = audioSampling(song_names=["guoge", "molihua"], max_samples=1000)
    test_2 = audioSampling(song_names=["guoge", "molihua"], max_samples=4000)


def test_extractAllAudio():
    test_1 = extractAllAudio("all_seg")


if __name__ == "__main__":
    extractRun()
