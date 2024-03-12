# -*- coding: utf-8 -*-

"""所有跨文件的全局变量由本模块计算并赋值

其他模块需要使用本模块全局变量时，在模块开头导入本模块即可
例子：
    from setting import *...

"""

import os
import sys
import re
from pathlib import Path


# 在pycharm的用户环境变量配置好科大讯飞的APP_ID和secretkey
LFASR_APP_ID = os.getenv("LFASR_APP_ID")
LFASR_SECRETKEY = os.getenv("LFASR_SECRETKEY")

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # program root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

# data
DATA_DIR = ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw_data"
RESULT_DATA_DIR = DATA_DIR / "result_data"
SCP_DATA_DIR = DATA_DIR / "scp"
FREQ_CSV = "调号音符频率表.csv"
SONGNAME_CSV = "文件歌曲表.csv"
SCORE_CSV = "文件评分表.csv"
RESULT_CSV = "模型结果表.csv"
EVALUATE_CSV = "评估结果表.csv"
INDEX_CSV = "指标结果表.csv"

# eigen_json
EIGEN_DIR = ROOT / "eigen_json"

# audio
UPLOAD_FILE_DIR = ROOT / "audio"

# resultJson
DOWNLOAD_DIR = ROOT / "resultJson"

# lyrics
LYRICS_DIR = ROOT / "lyrics"

# resultAudio
AUDIO_DIR = ROOT / "resultAudio"

# json结果的名字后缀
OUTPUT_JSON_NAME = "orderResult.json"

# 预处理后的audio的后缀
OUTPUT_AUDIO_NAME = "seg.wav"

# 测试脚手架
TEST_DIR = ROOT / "test_space"
TEST_AUDIO_DIR = TEST_DIR / "audio"
TEST_EIGEN_DIR = TEST_DIR / "eigen_json"
TEST_RESULT_DIR = TEST_DIR / "orderResult_example"
TEST_AUDIO_EIGEN_DIR = TEST_DIR / "audio_eigen_test"
TEST_DATA_DIR = TEST_DIR / "data"
TEST_RAWDATA_DIR = TEST_DATA_DIR / "raw_data"
TEST_RESULTDATA_DIR = TEST_DATA_DIR / "result_data"
