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
    """
    该函数旨在通过滑动窗口方式计算字符串a_str每次去掉第一个字符后与字符串b_str之间的Levenshtein距离，
    找到具有最小编辑距离的子串在a_str中的起始索引。

    参数:
    a_str (str): 待查找局部最小子串的源字符串
    b_str (str): 目标字符串，用于与a_str的子串进行比较

    返回:
    min_index (int or None): 编辑距离最小的a_str子串在原字符串中的起始索引，如果没有找到符合条件的子串，则返回None
    """

    # 初始化最小编辑距离为正无穷大，初始最小索引为空
    min_distance = float("inf")
    min_index = None

    # 遍历a_str的每个字符（实质上是遍历一次）
    for i in range(len(a_str)):
        # 计算当前a_str与b_str之间的Levenshtein距离
        distance = Levenshtein.distance(a_str, b_str)

        # 如果当前编辑距离小于已知的最小距离，则更新最小距离和最小索引
        if distance < min_distance:
            min_distance = distance
            min_index = i

        if len(a_str) > 1:
            a_str = a_str[1:]

    return min_index


# TODO: 当前阶段由于缺少乐理json文件，临时直接从txt文件获取歌词代替
def extract_lyrics_contents(folder_path, style=1):
    """
    该函数用于从指定文件夹路径中读取所有.txt结尾的文件，并提取其中的纯中文歌词内容。
    之后对提取的歌词内容进行进一步处理（根据style参数决定处理方式），
    最后返回一个字典，键为不含扩展名的文件名，值为处理后的歌词内容。

    参数:
    folder_path (str): 指定包含歌词文件的文件夹路径
    style (int, 默认为1): 控制歌词内容处理方式的参数，这里使用gbkXfrFstLetter函数对歌词进行特定风格转换

    返回:
    txt_contents_without_dot (dict): 字典类型，键为不包含"."的文件名，值为经过处理后的中文歌词内容
    """

    # 初始化一个空字典，用于存储歌词内容
    txt_contents = {}

    # 遍历指定文件夹下的所有文件
    for filename in os.listdir(folder_path):
        # 判断文件是否为.txt文件
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                # 获取文件名（不含扩展名）
                file_name_without_extension = os.path.splitext(filename)[0]
                content = file.read()

                # 使用正则表达式清除非中文字符，仅保留中文内容
                chinese_content = re.sub(r"[^\u4e00-\u9fa5]+", "", content)

                # 根据style参数对歌词内容进行首字母处理
                chinese_content = gbkXfrFstLetter(chinese_content, style)

                # 将处理后的中文歌词内容存入txt_contents字典中
                txt_contents[file_name_without_extension] = chinese_content

    # 过滤掉txt_contents字典中键中包含"."的项，生成新字典txt_contents_without_dot
    txt_contents_without_dot = {k: v for k, v in txt_contents.items() if "." not in k}

    return txt_contents_without_dot


def audio_catog(ad_json, lyrics_dict, acceptance_threshold: float = 0.7):
    """
    该函数接收一个音频ASR识别结果（ad_json）以及一个歌词字典（lyrics_dict），
    并计算音频识别文本与歌词库中每个歌曲歌词的余弦相似度。

    阈值设定为0.7，旨在过滤因识别错误或重复演唱导致的误匹配情况；
    若允许一定误差率，可考虑将阈值降低至0.65。

    参数:
    ad_json (dict): 包含音频文件关键信息及ASR识别文本的字典
    lyrics_dict (dict): 键为歌曲名，值为对应歌词文本的字典
    acceptance_threshold (float, 默认为0.7): 相似度判断阈值，只有当相似度大于等于此阈值时才认为匹配成功

    返回:
    csv_dict (dict): 当最大相似度超过阈值时，返回一个CSV格式的数据字典，包含匹配成功的音频文件名和对应的歌曲名
                     （注：若需要，还可以添加相似度分值，但当前版本未包括此项）
    """

    # 从ad_json中获取音频文件名
    audio_name = ad_json["key"]

    # 对ASR识别文本进行首字母转换处理
    asr_text = gbkXfrFstLetter(ad_json["text"], 1)

    # 初始化存储最终CSV输出的字典和存储相似度的字典
    csv_dict = {}
    dist_dict = {}

    # 计算并存储每首歌曲歌词与ASR文本之间的相似度
    for lkey in lyrics_dict.keys():
        song_name = lkey
        lyrics_text = lyrics_dict[lkey]
        dist = calculate_cosine_similarity(asr_text, lyrics_text)
        dist_dict[song_name] = dist

    # 找出相似度最高的歌曲
    max_key = max(dist_dict, key=dist_dict.get)

    # 判断最高相似度是否达到接受阈值，若达到则填充csv_dict并返回
    if dist_dict[max_key] >= acceptance_threshold:
        csv_dict["文件名"] = audio_name
        csv_dict["曲目"] = max_key
        # 可选地，可以将最大相似度值添加到csv_dict中，此处已注释掉
        # csv_dict["dist"] = dist_dict[max_key]

        return csv_dict


# 定义批量处理音频分类函数batch_audio_catog，该函数主要负责通过ASR结果和歌词内容进行音频分类
def batch_audio_catog(scp_name: str):
    """
    对音频批量曲目分类，并将分类结果保存到指定CSV文件中

    参数:
    scp_name (str): 指定音频文件的scp文件名

    返回:
    audio_catog_list (list): 包含所有音频文件的分类结果（CSV格式数据）的列表
    """

    # 调用funasrRun函数获取音频ASR识别结果列表
    rs_dict = funasrRun(scp_name=scp_name, input_mode="scp")

    # 提取歌词内容，生成歌词字典
    lyrics_dict = extract_lyrics_contents(EIGEN_DIR)

    # 封装audio_catog函数，使其具有默认的歌词字典参数
    audio_catog_new = partial(audio_catog, lyrics_dict=lyrics_dict)

    # 并行处理音频分类任务，生成分类结果列表
    audio_catog_list = multipuleProcess(audio_catog_new, rs_dict["scp_rs"])

    # 过滤掉结果列表中的空值
    audio_catog_list = [d for d in audio_catog_list if d]
    writeCsv(audio_catog_list, RAW_DATA_DIR, SONGNAME_CSV)

    return audio_catog_list


# 定义音频剪辑函数audio_seg，该函数基于歌词内容和广告信息对指定音频片段进行剪辑，并允许设置时间偏移量
def audio_seg(csv_dict, lyrics_dict, ad_dict, time_offset=150, scp_name=None):
    """
    音频剪辑函数，对音频文件进行剪辑，保留演唱部分，并保存至指定目录

    参数:
    csv_dict (dict): 包含音频文件基本信息的字典
    lyrics_dict (dict): 存储了歌曲名与歌词内容映射关系的字典
    ad_dict (dict): 存储了广告信息的字典，其中键是音频文件名，值包含广告文本等信息
    time_offset (int): 默认为150毫秒的时间偏移量，用于提前或延后剪辑起点
    scp_name (str): 可选参数，指明scp文件名，用于定位上传的原始音频文件路径
    """

    # 获取csv字典中音频文件的完整文件名
    file = csv_dict["文件名"]
    file_name = file + ".mp3"

    # 检查音频文件是否已剪辑并保存，如果不存在则执行剪辑操作
    if not os.path.exists(AUDIO_DIR / file_name):
        # 获取曲目名并在歌词字典中查找对应的歌词文本
        song = csv_dict["曲目"]
        song_text = lyrics_dict[song]

        # 从ASR识别结果字典中提取当前音频文件的识别文本
        ad_info = ad_dict[file]
        audio_text = gbkXfrFstLetter(ad_info["text"], 2)  # 对广告文本进行特定处理

        # 寻找识别结果与歌曲歌词之间的局部最小相似度索引，作为剪辑索引点
        min_index = find_local_minimum(audio_text, song_text)

        # 如果最小相似度索引<=1，则将时间偏移量设为0
        if min_index <= 1:
            time_offset = 0

        # 计算实际剪辑开始时间（减去时间偏移量，开头留白）
        start_time = ad_info["timestamp"][min_index][0] - time_offset

        # 执行音频剪辑操作
        cutAudio(
            start_time=start_time,
            output_dir=AUDIO_DIR,
            input_audio=UPLOAD_FILE_DIR / scp_name / file_name,  # 组合原始音频文件的完整路径
        )


# 定义批量音频剪辑函数batch_audio_seg，该函数基于歌曲CSV文件、歌词文件夹和ASR识别结果批量剪辑音频片段
def batch_audio_seg(
    song_csv_dir=RAW_DATA_DIR / SONGNAME_CSV, lyrics_dir=EIGEN_DIR, scp_name=None
):
    """
    批量剪辑音频的开头非演唱部分，并将剪辑后的音频保存于指定目录。

    参数:
    song_csv_dir (Path): 指定歌曲CSV文件的路径，默认位于RAW_DATA_DIR下的SONGNAME_CSV文件
    lyrics_dir (Path): 指定歌词文件夹的路径，默认为EIGEN_DIR
    scp_name (Optional[str]): 可选参数，指明scp文件名，用于定位上传的原始音频文件路径，默认为None
    """

    # 读取CSV文件并转换为字典列表
    csv_pd = pd.read_csv(song_csv_dir, encoding="gbk")
    csv_dict = csv_pd.to_dict("records")

    # 提取并处理歌词内容，生成歌词字典
    lyrics_dict = extract_lyrics_contents(lyrics_dir, style=2)

    # 调用funasrRun函数获取音频文件的ASR识别结果并整理成字典格式
    rs_dict = funasrRun(scp_name=scp_name, input_mode="scp")
    audio_json_list = rs_dict["scp_rs"]
    dict_indexed = {
        d["key"]: {"text": d["text"], "timestamp": d["timestamp"]}
        for d in audio_json_list
    }

    # 封装audio_seg函数，实例化固定参数
    audio_seg_new = partial(
        audio_seg, scp_name=scp_name, ad_dict=dict_indexed, lyrics_dict=lyrics_dict
    )

    # 使用多线程并行调用封装后的audio_seg_new函数，处理每一个CSV字典项
    multipuleThread(audio_seg_new, csv_dict)


def audio_pre_cat_seg(scp_name, mode):
    if mode == "catog":
        batch_audio_catog(scp_name)
    elif mode == "seg":
        batch_audio_seg(scp_name)


if __name__ == "__main__":
    audio_pre_cat_seg("all_audio", "seg")
