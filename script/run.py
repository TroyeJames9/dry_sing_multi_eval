# -*- coding: utf-8 -*-
import os
import sys
import re
import glob
import time
import concurrent.futures
import asyncio
import aiohttp
from pathlib import Path
from lfasr_new import downloadOrderResult, getTransferResult, getCutPoint, getCpTimestamp, cutAudio, extractLyrics, \
    gbkXfrFstLetter
from articulation_analysis import calculate_cosine_similarity

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


def extractLyricsPart(
        upload_file_path=UPLOAD_FILE_DIR / 'song_demo.mp3',
        lyrics_file_name='song_demo.txt',
        is_cut=True,
        is_download_seg=False,
        cut_style=2,
        extract_style=0,
        match_str_size=20,
        threshold=0.6,
        app_id=LFASR_APP_ID,
        secret_key=LFASR_SECRETKEY,
        download_dir=DOWNLOAD_DIR,
        output_json_name=OUTPUT_JSON_NAME,
        lyrics_dir=LYRICS_DIR,
        audio_dir=AUDIO_DIR,
        output_audio_name=OUTPUT_AUDIO_NAME
):
    result_json = downloadOrderResult(
        appid=app_id,
        secret_key=secret_key,
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
            w_str_result=w_str_result, file_name=lyrics_file_name, match_str_size=match_str_size, lyrics_dir=lyrics_dir,
            threshold=threshold)
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
        lyrics_dir=LYRICS_DIR,
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


def loopExtractLyricsPartV1(audio_song_name):
    folder_path = UPLOAD_FILE_DIR / audio_song_name
    lyrics_file_name = audio_song_name + '.txt'
    mp3_files = glob.glob(os.path.join(folder_path, '*.mp3'))
    for file_path in mp3_files:
        lyrics_part_str = extractLyricsPart(upload_file_path=file_path,
                                            lyrics_file_name=lyrics_file_name,
                                            is_cut=False)
        print(
            calcCosineSimilarity(input_audio_str=lyrics_part_str, lyrics_file_name=lyrics_file_name, vectorizer_type=0))


async def asyncioExtractLyricsPart(upload_file_path, lyrics_file_name, is_cut, semaphore):
    async with semaphore:
        return await extractLyricsPart(upload_file_path=upload_file_path, lyrics_file_name=lyrics_file_name,
                                       is_cut=is_cut)


async def concurrentTask(upload_file_paths, lyrics_file_name, is_cut, max_concurrency):
    semaphore = asyncio.Semaphore(max_concurrency)

    tasks = [
        asyncioExtractLyricsPart(upload_file_path=upload_file_path, lyrics_file_name=lyrics_file_name, is_cut=is_cut,
                                 semaphore=semaphore)
        for upload_file_path in upload_file_paths
    ]

    results = await asyncio.gather(*tasks)

    return results


def asyncExtractLyricsPartV2(audio_song_name):
    folder_path = UPLOAD_FILE_DIR / audio_song_name
    lyrics_file_name = audio_song_name + '.txt'
    mp3_files = glob.glob(os.path.join(folder_path, '*.mp3'))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        concurrentTask(upload_file_paths=mp3_files, lyrics_file_name=lyrics_file_name, is_cut=False,
                       max_concurrency=18))


def threadExtractLyricsPartV3(audio_song_name):
    folder_path = UPLOAD_FILE_DIR / audio_song_name
    lyrics_file_name = audio_song_name + '.txt'
    mp3_files = glob.glob(os.path.join(folder_path, '*.mp3'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        # 使用map方法并发执行 downloadOrderResult 函数
        upload_file_paths = mp3_files
        executor.map(lambda x: extractLyricsPart(lyrics_file_name=lyrics_file_name, is_cut=False, upload_file_path=x),
                     upload_file_paths
                     )


def run():
    pass


def test_loop_vs_multithread():
    start_time_V1 = time.time()
    loopExtractLyricsPartV1('fenHongSeDeHuiYi')
    end_time_V1 = time.time()
    input("请删除resultJson里由v1生成的json，删除完输入y")
    start_time_V3 = time.time()
    threadExtractLyricsPartV3('fenHongSeDeHuiYi')
    end_time_V3 = time.time()
    print('v1 consume', end_time_V1 - start_time_V1, '\nv3 consume', end_time_V3 - start_time_V3)


if __name__ == '__main__':
    # threadExtractLyricsPartV3('fenHongSeDeHuiYi')
    # test_loop_vs_multithread()

    pass
