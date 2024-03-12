# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
from setting import *

# noinspection PyUnresolvedReferences
from util import *

# noinspection PyUnresolvedReferences
import Levenshtein
from functools import partial
from run.run_v2 import *
from preprocess.prep_audio import *


def find_local_minimum(a_str, b_str):
    min_distance = float("inf")
    min_index = None

    for i in range(len(a_str)):
        distance = Levenshtein.distance(a_str, b_str)
        if distance < min_distance:
            min_distance = distance
            min_index = i
        if len(a_str) > 1:
            a_str = a_str[1:]

    return min_index


def extract_lyrics_contents(folder_path, style=1):
    """temp：由于目前还未补充国歌以外的乐理json文件，所以暂时直接从txt获取歌词来替代从json获取"""
    txt_contents = {}

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                file_name_without_extension = os.path.splitext(filename)[0]
                content = file.read()
                # 使用正则表达式只保留中文字符
                chinese_content = re.sub(r"[^\u4e00-\u9fa5]+", "", content)
                chinese_content = gbkXfrFstLetter(chinese_content, style)
                txt_contents[file_name_without_extension] = chinese_content
    txt_contents_without_dot = {k: v for k, v in txt_contents.items() if "." not in k}

    return txt_contents_without_dot


def audio_catog(ad_json, lyrics_dict, acceptance_threshold: float = 0.7):
    """阈值设置为0.7是为了过滤掉所有可能识别错（比如《茉莉花》和《x花》)、重复演唱的情况，如果允许容错则建议设置为0.65。"""
    audio_name = ad_json["key"]
    asr_text = gbkXfrFstLetter(ad_json["text"], 1)
    csv_dict = {}
    dist_dict = {}
    for lkey in lyrics_dict.keys():
        song_name = lkey
        lyrics_text = lyrics_dict[lkey]
        dist = calculate_cosine_similarity(asr_text, lyrics_text)
        dist_dict[song_name] = dist
    max_key = max(dist_dict, key=dist_dict.get)
    if dist_dict[max_key] >= acceptance_threshold:
        csv_dict["文件名"] = audio_name
        csv_dict["曲目"] = max_key
        # csv_dict["dist"] = dist_dict[max_key]

        return csv_dict


def batch_audio_catog(scp_name: str):
    rs_dict = funasr_run(scp_name=scp_name, input_mode="scp")
    audio_json_list = rs_dict["scp_rs"]
    lyrics_dict = extract_lyrics_contents(EIGEN_DIR)
    audio_catog_new = partial(audio_catog, lyrics_dict=lyrics_dict)
    audio_catog_list = multipuleProcess(audio_catog_new, audio_json_list)
    audio_catog_list = [d for d in audio_catog_list if d]
    writeCsv(audio_catog_list, RAW_DATA_DIR, SONGNAME_CSV)

    return audio_catog_list


def audio_seg(csv_dict, lyrics_dict, ad_dict, time_offset=150, scp_name=None):
    file = csv_dict["文件名"]
    file_name = file + ".mp3"
    if not os.path.exists(AUDIO_DIR / file_name):
        song = csv_dict["曲目"]
        song_text = lyrics_dict[song]

        ad_info = ad_dict[file]
        audio_text = gbkXfrFstLetter(ad_info["text"], 2)

        min_index = find_local_minimum(audio_text, song_text)
        if min_index <= 1:
            time_offset = 0
        start_time = ad_info["timestamp"][min_index][0] - time_offset

        cutAudio(
            start_time=start_time,
            output_dir=AUDIO_DIR,
            input_audio=UPLOAD_FILE_DIR / scp_name / file_name,
        )


def batch_audio_seg(
    song_csv_dir=RAW_DATA_DIR / SONGNAME_CSV, lyrics_dir=EIGEN_DIR, scp_name=None
):
    csv_pd = pd.read_csv(song_csv_dir, encoding="gbk")
    csv_dict = csv_pd.to_dict("records")
    lyrics_dict = extract_lyrics_contents(lyrics_dir, style=2)

    rs_dict = funasr_run(scp_name=scp_name, input_mode="scp")
    audio_json_list = rs_dict["scp_rs"]
    dict_indexed = {
        d["key"]: {"text": d["text"], "timestamp": d["timestamp"]}
        for d in audio_json_list
    }
    audio_seg_new = partial(
        audio_seg, scp_name=scp_name, ad_dict=dict_indexed, lyrics_dict=lyrics_dict
    )
    multipuleThread(audio_seg_new, csv_dict)


def audio_pre_cat_seg(scp_name, mode):
    if mode == "catog":
        batch_audio_catog(scp_name)
    elif mode == "seg":
        batch_audio_seg(scp_name)


if __name__ == "__main__":
    audio_pre_cat_seg("all_audio", "seg")
