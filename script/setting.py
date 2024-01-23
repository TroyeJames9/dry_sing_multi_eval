# -*- coding: utf-8 -*-
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

UPLOAD_FILE_DIR = ROOT / "audio"
DOWNLOAD_DIR = ROOT / 'resultJson'
LYRICS_DIR = ROOT / "lyrics"
AUDIO_DIR = ROOT / "resultAudio"
OUTPUT_JSON_NAME = 'orderResult.json'
OUTPUT_AUDIO_NAME = "seg.mp3"
