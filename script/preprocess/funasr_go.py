# -*- coding: utf-8 -*-

"""
本模块是基于FunASR库实现的自动语音识别（ASR）功能模块。模块包含的主要功能有：

1. `funasrRun`：支持单个音频文件或SCP文件列表的语音识别，输出每个词语的时间戳信息，并以JSON格式保存识别结果。
2. `getWordInfoList`：将`funasrRun`的输出结果转换成结构化的数据格式，提供每个词语及其对应的开始和结束时间信息。

模块主要功能：
- `funasrRun`：模块的主入口，用于执行语音识别操作。
- `getWordInfoList`：处理`funasrRun`的输出结果，生成详细的词语信息列表。

经典使用案例
    rs_dict = funasrRun(input_audio_dataset="qilai", input_audio_name="cst.mp3")
    rs_dict_list = rs_dict["scp_rs"][0]
    eigen_dict = getWordInfoList(funasr_dict=rs_dict_list)
    print(eigen_dict)

本模块所使用的funASR算法相关资料：
    https://www.modelscope.cn/models/iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch/summary

"""
import io
import sys
from contextlib import contextmanager


@contextmanager
def suppress_stdout_stderr():
    new_stdout, new_stderr = io.StringIO(), io.StringIO()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_stdout, new_stderr
        yield None  # 这里是被抑制输出的代码块
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr


# 使用上下文管理器抑制funasr模块导入时的print输出
with suppress_stdout_stderr():
    from funasr import AutoModel  # 导入模块时的print语句会被抑制
import re
from pathlib import Path
from setting import *
import numpy as np
import json


def funasrRun(
        model: str = "iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch",  # 默认使用的ASR模型路径
        vad_model: str = "fsmn-vad",  # 默认使用的语音活动检测模型
        punc_model: str = "ct-punc-c",  # 默认使用的标点插入模型
        input_audio_dir: Path = UPLOAD_FILE_DIR,  # 输入音频文件所在的父目录，默认上传文件目录
        input_audio_dataset: str = None,  # 待识别音频所属的数据集名称
        input_audio_name: str = None,  # 待识别的音频文件名（含后缀）
        input_scp_dir: Path = SCP_DATA_DIR,  # SCP文件所在的目录，默认SCP数据目录
        scp_name: str = None,  # SCP文件名
        input_mode: str = "file",  # 输入数据模式，可选："file"（单个音频文件）或"scp"（SCP文件）
        download_json_dir: Path = DOWNLOAD_DIR,  # 输出结果JSON文件保存的父目录，默认下载目录
) -> dict:
    """
    使用funasr进行ASR（语音识别），输出识别文字以及每个字的时间戳。

    支持两种数据输入方式：
    1. 单个音频文件时，需要提供input_audio_dataset和input_audio_name参数。
    2. SCP文件时，需提供scp_name参数并将input_mode设置为"scp"。

    输出结果是一个字典，结构示例：
    {
        "scp_rs": [
            {"key": file_name, "text": asr_result, "timestamp": [[start,end],[start,end], ...]},
            {"key": file_name, "text": asr_result, "timestamp": [[start,end],[start,end], ...]},
            ...
        ]
    }

    参数：
        model (str): ASR模型路径，更多模型选择参考达摩院Paraformer large
        vad_model (str): 语音活动检测模型名称
        punc_model (str): 标点插入模型名称
        input_audio_dir (Path): 输入音频文件的上级目录
        input_audio_dataset (str): 音频文件所在的数据集名称
        input_audio_name (str): 音频文件名（含扩展名）
        input_scp_dir (Path): SCP文件所在的目录
        scp_name (str): SCP文件名
        input_mode (str): 输入模式，取值为 'file' 或 'scp'
        download_json_dir (Path): 输出结果JSON文件保存的目录

    返回值：符合上述结构的字典对象
    """
    # 如果输入的是单个音频文件，构建音频文件完整路径
    if input_audio_name is not None:
        path_str = str(input_audio_dir / input_audio_dataset / input_audio_name)
        download_dir = download_json_dir / input_audio_dataset

        # 创建输出结果保存目录（若不存在）
        if not download_dir.exists():
            download_dir.mkdir(parents=True)

        # 提取音频文件名（不含扩展名），并构建JSON结果文件名
        real_audio_name = re.sub(r"\..*", "", input_audio_name)
        json_name = real_audio_name + ".json"
        download_path = download_dir / json_name

    # 如果输入的是SCP文件，构建JSON结果文件名
    else:
        json_name = scp_name + ".json"
        download_path = download_json_dir / json_name

    # 若结果文件尚未生成，则执行ASR识别过程
    if not download_path.exists():

        # 初始化AutoModel，加载指定模型
        model = AutoModel(
            model=model,
            model_revision="v2.0.4",
            vad_model=vad_model,
            vad_model_revision="v2.0.4",
            punc_model=punc_model,
            punc_model_revision="v2.0.4",
        )

        # 根据输入模式分别调用模型进行识别
        if input_mode == "file":
            rs_list = model.generate(input=path_str, batch_size_s=300)
        elif input_mode == "scp":
            scp_name = scp_name + ".scp"
            scp_path = str(input_scp_dir / scp_name)
            rs_list = model.generate(input=scp_path, batch_size_s=300)

        # 将识别结果封装成字典并写入JSON文件
        rs_dict = {"scp_rs": rs_list}
        with open(download_path, "w", encoding="gbk") as json_file:
            json.dump(rs_dict, json_file, indent=2, ensure_ascii=False)

    # 如果结果文件已存在，直接读取并返回结果
    else:
        with open(download_path, "r", encoding="gbk") as file:
            rs_dict = json.load(file)

    return rs_dict


def getWordInfoList(funasr_dict: dict) -> dict:
    """
    根据funasr_run输出的结果生成一个名为'eigen_list'的字典列表，其中包含了每个字及其对应的开始时间和结束时间。

    示例输出可见于：ROOT / "orderResult_example" / "getWordInfoList_result.json"

    参数：
        funasr_dict(dict)：
            包含ASR识别结果及其时间戳信息的字典，由funasr_run函数生成

    返回：
        eigen_dict(dict)：
            结构定义如下：
            eigen_list - 一个字典组成的列表
                word(str)：单个汉字或英文字符
                eigen(dict) - 字的时间戳信息
                    start_time(float)：字的起始时间（单位：秒）
                    end_time(float)：字的结束时间（单位：秒）

    函数内部逻辑：
    1. 获取原始识别文本及其时间戳数组
    2. 清理文本，保留中文、英文字符及空格
    3. 遍历清理后的文本，逐字构造新字典结构，并填充时间戳信息
    """
    # 获取funasr_dict中的识别文本和时间戳数组
    text = funasr_dict["text"]
    timestamps = funasr_dict["timestamp"]

    # 正则表达式匹配规则：包含中文、英文字符和 中文、英文、空格结合。
    """troyejames：由于发现有概率识别出来英文，所以同时要包含大小写英文以及空格"""
    c_pattern = re.compile(r'[\u4e00-\u9fa5]')  # 中文字符正则
    e_pattern = re.compile(r'[a-zA-Z]')  # 英文字符正则
    pattern = re.compile(r"[^ \u4e00-\u9fa5a-zA-Z]+")  # 去除非中文、非英文、非空格字符
    clean_text = pattern.sub("", text)  # 清理文本至仅包含有效字符

    # 初始化返回的字典结构
    eigen_dict = {"eigen_list": []}

    j = 0
    i = 0

    # 遍历清理后的文本
    while i <= len(clean_text) - 1:
        # 初始化当前字的信息项
        eigen_dict_item = {"word": "", "eigen": {}}
        eigen = eigen_dict_item["eigen"]

        # 判断当前字符是否为中文或英文
        if c_pattern.match(clean_text[i]):
            eigen_dict_item["word"] = clean_text[i]
        elif e_pattern.match(clean_text[i]):
            # 对于英文单词，连续合并多个字母
            eigen_dict_item["word"] = clean_text[i]
            i += 1
            while (i <= len(clean_text) - 1) and e_pattern.match(clean_text[i]):
                eigen_dict_item["word"] = eigen_dict_item["word"] + clean_text[i]
                i += 1
            # 回退一位以便继续遍历
            i -= 1
        else:
            # 跳过非中文非英文字符(比如空格）
            i += 1
            continue

        # 设置当前字的起始时间
        eigen["start_time"] = round(timestamps[j][0] / 1000, 3)

        # 判断相邻字之间的时间间隔，如果小于2秒则将下一个时间区间的start_time作为本区间的结束时间
        if (i < len(clean_text) - 1) and (timestamps[j + 1][0] - timestamps[j][1] <= 2000):
            eigen["end_time"] = round(timestamps[j + 1][0] / 1000, 3)
        else:
            eigen["end_time"] = round(timestamps[j][1] / 1000, 3)

        j += 1
        i += 1

        # 将当前字的时间戳信息添加到返回结果中
        eigen_dict["eigen_list"].append(eigen_dict_item)

    return eigen_dict


if __name__ == "__main__":
    # rs_dict = funasr_run(song_name="guoge", input_mode="scp")
    rs_dict = funasrRun(input_audio_dataset="qilai", input_audio_name="qilai.wav")
    rs_dict_list = rs_dict["scp_rs"][0]
    eigen_dict = getWordInfoList(funasr_dict=rs_dict_list)
    print(eigen_dict)
