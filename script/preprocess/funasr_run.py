# -*- coding: utf-8 -*-

"""pass

pass

"""

from pathlib import Path
from setting import *
from funasr import AutoModel


def funasr_run(
    model: str = "iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
    vad_model: str = "fsmn-vad",
    punc_model: str = "ct-punc-c",
    input_audio_dir: Path = UPLOAD_FILE_DIR,
    input_audio_dataset: str = None,
    input_audio_name: str = None,
):
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

    返回：
        rs_list(list):
            只有一个元素的列表，元素为字典，结构如下：
                key（str）:
                    随机种子
                text（str）:
                    识别文本
                timestamp(list):
                    识别文本每个字的时间戳
    """
    path_str = str(input_audio_dir / input_audio_dataset / input_audio_name)
    model = AutoModel(
        model=model,
        model_revision="v2.0.4",
        vad_model=vad_model,
        vad_model_revision="v2.0.4",
        punc_model=punc_model,
        punc_model_revision="v2.0.4",
    )
    rs_list = model.generate(input=path_str, batch_size_s=300)
    return rs_list
