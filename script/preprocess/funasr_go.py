# -*- coding: utf-8 -*-

"""pass

pass

"""

from pathlib import Path
from setting import *
import numpy as np
import json
from funasr import AutoModel


def funasr_run(
    model: str = "iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
    vad_model: str = "fsmn-vad",
    punc_model: str = "ct-punc-c",
    input_audio_dir: Path = UPLOAD_FILE_DIR,
    input_audio_dataset: str = None,
    input_audio_name: str = None,
    input_parsed_audio: np.ndarray = None,
    input_mode: str = "file",
    download_json_dir: Path = DOWNLOAD_DIR,
) -> dict:
    """使用funasr进行ASR（语音识别）,输出识别文字以及每个字的时间戳

    参数：
        model(str):
            选用的模型，默认为"iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch"，如何选择模型详见达摩院Paraformer large
        vad_model(str):
            语音活动检测选用的模型，默认为fsmn-vad
        punc_model(str):
            标点检测选用的模型，默认为ct-punc-c
        input_audio_dir(Path):
            待识别音频所处的爷目录，默认为UPLOAD_FILE_DIR
        input_audio_dataset(str):
            待识别音频所处的数据集名称
        input_audio_name(str):
            音频文件名（带后缀）
        input_parsed_audio(np.ndarray):
            已解析的audio信号序列
        input_mode(str):
            输入的形式，包括：
                file：输入音频文件
                parsed：输入已解析的audio信号序列
        download_json_dir(Path):
            输出结果保存为json的爷目录，默认为DOWNLOAD_DIR

    返回：
        rs_dict(dict):
            只有一个元素的列表，元素为字典，结构如下：
                key（str）:
                    随机种子
                text（str）:
                    识别文本
                timestamp(list):
                    识别文本每个字的时间戳
    """
    if input_audio_name is not None:
        path_str = str(input_audio_dir / input_audio_dataset / input_audio_name)
    download_dir = download_json_dir / input_audio_dataset
    if not download_dir.exists():
        download_dir.mkdir(parents=True)

    real_audio_name = re.sub(r"\..*", "", input_audio_name)
    json_name = real_audio_name + ".json"
    download_path = download_dir / json_name

    if not download_path.exists():
        model = AutoModel(
            model=model,
            model_revision="v2.0.4",
            vad_model=vad_model,
            vad_model_revision="v2.0.4",
            punc_model=punc_model,
            punc_model_revision="v2.0.4",
        )
        if input_mode == "file":
            rs_list = model.generate(input=path_str, batch_size_s=300)
        elif input_mode == "parsed":
            rs_list = model.generate(input=input_parsed_audio, batch_size_s=300)

        with open(download_path, "w", encoding="gbk") as json_file:
            json.dump(rs_list[0], json_file, indent=2, ensure_ascii=False)
    else:
        with open(download_path, "r", encoding="gbk") as file:
            rs_dict = json.load(file)

    return rs_dict


def getWordInfoList(funasr_dict: dict) -> dict:
    """提供类似funasr_run输出结果的列表，生成一个eigen_list字典

    详细生成结果例子见ROOT / "orderResult_example"   / "getWordInfoList_result.json"

    参数：
        funasr_dict(dict)：
            funasr_run输出结果形式的列表

    返回：
        eigen_dict(dict)：
            结构如下：
            eigen_list(list[dict])
                    word(str):字
                    eigen(dict)
                        start_time(float)
                        end_time(float)
    """
    text = funasr_dict["text"]
    time = funasr_dict["timestamp"]
    text = re.sub(r"[^\u4e00-\u9fa5\d]+", "", text)

    eigen_dict = {"eigen_list": []}

    for i in range(len(text)):
        eigen_dict[i] = {}

        eigen_dict[i]["word"] = text[i]

        # 检验与下一个字之间的时间差，<2秒则意味着中间无明显间隔
        if i < len(text) - 1:
            eigen_dict[i]["start_time"] = time[i][0]
            if time[i + 1][0] - time[i][1] <= 2000:
                eigen_dict[i]["end_time"] = time[i + 1][0]
            else:
                eigen_dict[i]["end_time"] = time[i][1]

    return eigen_dict


if __name__ == "__main__":
    rs_dict = funasr_run(input_audio_dataset="qilai", input_audio_name="cst.mp3")
    eigen_dict = getWordInfoList(funasr_dict=rs_dict)
    print(eigen_dict)