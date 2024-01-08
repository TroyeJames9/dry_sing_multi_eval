# -*- coding: utf-8 -*-
import os
import sys
import re
from pathlib import Path
from lfasr_new import downloadOrderResult, getTransferResult, getCutPoint, getCpTimestamp, cutAudio, extractLyrics, gbkXfrFstLetter
from articulation_analysis import calculate_cosine_similarity

# 在pycharm的用户环境变量配置好科大讯飞的APP_ID和secretkey
LFASR_APP_ID = os.getenv("LFASR_APP_ID")
LFASR_SECRETKEY = os.getenv("LFASR_SECRETKEY")

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # program root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

lfasr_host = 'https://raasr.xfyun.cn/v2/api'
# 请求的接口名
api_upload = '/upload'
api_get_result = '/getResult'


def extractLyricsPart(
        upload_file_dir=ROOT / "audio",
        download_dir=ROOT / 'resultJson',
        audio_dir=ROOT / "resultAudio",
        upload_file_name='song_demo.mp3',
        output_json_name='orderResult.json',
        lyrics_file_name='song_demo.txt',
        output_audio_name="song_demo_seg.mp3",
        is_cut=True,
        is_download_seg=False,
        cut_style=2,
        extract_style=0,
        match_str_size=20
):
    upload_file_path = upload_file_dir / upload_file_name
    result_json = downloadOrderResult(
        upload_file_path=upload_file_path,
        download_dir=download_dir,
        output_file_name=output_json_name)
    w_str_result = getTransferResult(result_json, style=cut_style)

    raw_extract_result = getTransferResult(result_json, style=extract_style)
    pattern = re.compile(r'[^\u4e00-\u9fa5]')
    extract_result = re.sub(pattern, '', raw_extract_result)
    start_cut_point, end_cut_point = 0, len(extract_result)

    if is_cut:
        start_cut_point, end_cut_point = getCutPoint(
            w_str_result=w_str_result, file_name=lyrics_file_name, match_str_size=match_str_size)
        if is_download_seg:
            s_cut_point_t = getCpTimestamp(
                result_json,
                start_cut_point,
                is_end=False) - 0.2
            e_cut_point_t = getCpTimestamp(
                result_json,
                end_cut_point,
                is_end=True) + 0.2
            print(
                "start time is", round(s_cut_point_t, 1),
                "s,end_time is", round(e_cut_point_t, 1), "s")
            cutAudio(
                start_time=s_cut_point_t,
                end_time=e_cut_point_t,
                output_dir=audio_dir,
                output_audio=output_audio_name,
                input_audio=upload_file_path)
    lyrics_part_str = extract_result[int(
        start_cut_point):int(end_cut_point + 1)]
    return lyrics_part_str


def calcCosineSimilarity(
        input_audio_str,
        lyrics_dir='lyrics',
        lyrics_file_name='song_demo.txt',
        style=1,
        vectorizer_type=0):
    input_audio_str = gbkXfrFstLetter(input_audio_str, style=1)
    lyrics = extractLyrics(
        lyrics_dir=lyrics_dir,
        file_name=lyrics_file_name,
        style=style)
    similarity_score = calculate_cosine_similarity(
        input_audio_str, lyrics, vectorizer_type=vectorizer_type)
    return similarity_score


def run():
    lyrics_part_str = extractLyricsPart()
    similarity_score = calcCosineSimilarity(
        input_audio_str=lyrics_part_str, vectorizer_type=1)


if __name__ == '__main__':
    run()
