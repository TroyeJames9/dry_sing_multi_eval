# -*- coding: utf-8 -*-

"""调用科大讯飞的语音转写API提取转写结果

API说明详见“https://www.xfyun.cn/doc/asr/ifasr_new/API.html” 。
API转写结果的json结构详见 https://mubu.com/doc/5ZN7PfUKD9Y 的“解析API的orderResult json字符串”

"""

import base64
import hashlib
import hmac
import json
import os
import time
import requests
import urllib
import sys
import re
import doctest
from pathlib import Path
from pydub import AudioSegment
from pypinyin import pinyin, lazy_pinyin, Style

lfasr_host = "https://raasr.xfyun.cn/v2/api"
# 请求的接口名
api_upload = "/upload"
api_get_result = "/getResult"


class RequestApi(object):
    """调用科大讯飞的语音转写API，从API获得json形式的转写结果

    API说明详见“https://www.xfyun.cn/doc/asr/ifasr_new/API.html” 。
    设定的属性可以根据API可选参数来继续扩充，troyejames9根据本项目需求添加了hotword属性。

    属性：
        appid：
            科大讯飞个人账号的应用id，需在https://www.xfyun.cn/的控制台新建应用来获取appid。
        secret_key：
            科大讯飞应用id对应的密钥。
        upload_file_path：
            音频文件的绝对路径，可选格式包括mp3,wav,pcm,aac,opus,flac,ogg,
            m4a,amr,speex（微信）,lyb,ac3,aac,ape,m4r,mp4,acc,wma。
        hotword：
            热词，用以提升专业词汇的识别率，格式为“热词1| 热词2| 热词3”，
            单个热词长度为[2,16]，热词个数限制 200个。
    """

    def __init__(self, appid, secret_key, upload_file_path, hotword):
        self.appid = appid
        self.secret_key = secret_key
        self.upload_file_path = upload_file_path
        self.ts = str(int(time.time()))
        self.signa = self.get_signa()
        self.hotword = hotword

    def get_signa(self):
        """根据appid和secret_key生成鉴权字符串signa。"""
        appid = self.appid
        secret_key = self.secret_key
        m2 = hashlib.md5()
        m2.update((appid + self.ts).encode("utf-8"))
        md5 = m2.hexdigest()
        md5 = bytes(md5, encoding="utf-8")
        # 以secret_key为key, 上面的md5为msg， 使用hashlib.sha1加密结果为signa
        signa = hmac.new(secret_key.encode("utf-8"), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, "utf-8")
        return signa

    def upload(self):
        """将属性及其得到的参数进行传参，调用语音转写API。

        返回：
            json格式的upload_result，具体键值对详见
            “https://www.xfyun.cn/doc/asr/ifasr_new/API.html#%E6%8E%A5%E5%8F%A3%E8%AF%B4%E6%98%8E” 。
        """
        print("upload part：")
        upload_file_path = self.upload_file_path
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)

        param_dict = {}
        param_dict["appId"] = self.appid
        param_dict["signa"] = self.signa
        param_dict["ts"] = self.ts
        param_dict["fileSize"] = file_len
        param_dict["fileName"] = file_name
        param_dict["duration"] = "200"  # 没严格限制，无需修改
        param_dict["language"] = "cn"  # 选择语言
        param_dict["languageType"] = 4  # 语言识别模式选择,4为纯中文模式
        param_dict["hotWord"] = self.hotword  # 热词
        """
        以下为部分额外可选的传入参数，可根据需要以此形式添加参数
        可选参数详见https://www.xfyun.cn/doc/asr/ifasr_new/API.html
        """
        # param_dict["candidate"] = ""
        # param_dict["roleType"] = ""
        # param_dict["roleNum"] = ""
        # param_dict["roleNum"] = ""
        # param_dict["pd"] = ""
        # param_dict["audioMode"] = ""
        print("upload param：", param_dict)
        data = open(upload_file_path, "rb").read(file_len)

        response = requests.post(
            url=lfasr_host + api_upload + "?" + urllib.parse.urlencode(param_dict),
            headers={"Content-type": "application/json"},
            data=data,
        )
        print("upload_url:", response.request.url)
        upload_result = json.loads(response.text)
        print("upload resp:", upload_result)
        return upload_result

    def get_result(self):
        """调用科大讯飞API获取json格式的转写结果。

        根据upload方法输出的order_Id来调用API获取order_id对应的转写结果，调用频率设定为每秒1次，
        每秒最大并发量为18，根据API返回的json结果中的status键的值来确定API状态，如果status等于4
        则意味着转写完成，返回json结果。

        返回：
            json格式的转写结果，键值对详见
            “https://www.xfyun.cn/doc/asr/ifasr_new/API.html” 。
        """
        uploadresp = self.upload()
        orderId = uploadresp["content"]["orderId"]
        param_dict = {}
        param_dict["appId"] = self.appid
        param_dict["signa"] = self.signa
        param_dict["ts"] = self.ts
        param_dict["orderId"] = orderId
        param_dict["resultType"] = "transfer"
        print("")
        print("get_result part：")
        print("get_result parm：", param_dict)
        status = 3
        # 建议使用回调的方式查询结果，查询接口有请求频率限制
        while status == 3:
            response = requests.post(
                url=lfasr_host
                + api_get_result
                + "?"
                + urllib.parse.urlencode(param_dict),
                headers={"Content-type": "application/json"},
            )
            # print("get_result_url:",response.request.url)
            result = json.loads(response.text)
            print(result)
            status = result["content"]["orderInfo"]["status"]
            print("status=", status)
            if status == 4 and status == -1:
                break
            time.sleep(1)  # 每隔一秒调用一次API
        return result


def downloadOrderResult(
    appid: str,
    secret_key: str,
    lyrics_dir: Path,
    lyrics_file_name: str,
    upload_file_path: Path,
    download_dir: Path,
    output_file_name: str,
) -> dict:
    """调用RequestApi类来获取音频转写的json格式字符串结果。

    首先提取音频名，结合output_file_name来对json结果文件进行命名，
    下载之前判断json结果文件的绝对路径是否存在，如不存在才调用API，
    然后根据json的结构去提取orderResult的识别结果内容。
    json结构详见https://mubu.com/doc/5ZN7PfUKD9Y 的“解析API的orderResult json字符串” 。

    参数：
        appid(str)：
            科大讯飞个人账号的应用id，需在https://www.xfyun.cn/的控制台新建应用来获取appid。
        secret_key(str)：
            科大讯飞应用id对应的密钥。
        lyrics_dir(Path)：
            歌词文件目录的绝对路径。
        lyrics_file_name(str)：
            歌词文件名称，歌词用于制作热词。
        upload_file_path(Path)：
            音频文件的绝对路径，可选格式包括mp3,wav,pcm,aac,opus,flac,ogg,
            m4a,amr,speex（微信）,lyb,ac3,aac,ape,m4r,mp4,acc,wma。
        download_dir(Path)：
            json结果文件下载的所在目录。
        output_file_name(str)：
            json结果文件的名称后缀，用来与音频文件名拼接得到json结果文件名。

    返回：
        转写结果的json数据，提取了结果中['content']→['orderResult']→["lattice"]键。
        输出实例见orderResult_example/orderResult_lattice.json。
    """
    file_name = os.path.basename(upload_file_path)
    real_file_name = re.search(r"^(.*?)\.", file_name).group(1)
    new_output_file_name = real_file_name + "_" + output_file_name
    download_path = download_dir / new_output_file_name
    # 判断音频的json文件是否已经存在，已存在则不执行下载操作
    if not os.path.exists(download_path):
        print(f"Start download '{download_path}' ...")
        # 检查下载目录是否存在，如果不存在则创建该目录
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            print(f"Path '{download_dir}' created.")
        else:
            print(f"Path '{download_dir}' already exists.")
        hotword = getHotWords(lyrics_dir=lyrics_dir, file_name=lyrics_file_name)
        api = RequestApi(
            appid=appid,
            secret_key=secret_key,
            upload_file_path=upload_file_path,
            hotword=hotword,
        )
        transfer_result = api.get_result()
        # 获取transfer_result结果中content下orderResult的字符串内容
        orderResult_str = transfer_result["content"]["orderResult"]
        orderResult_json = json.loads(orderResult_str)
        lattice_json = orderResult_json["lattice"]
        # 将JSON数据保存到本地
        with open(download_path, "w", encoding="gbk") as json_file:
            json.dump(lattice_json, json_file, indent=2, ensure_ascii=False)
        print(f"File '{download_path}' created!")
    else:
        print(f"File '{download_path}' already exists!Download is close...")
    with open(download_path, "r", encoding="gbk") as file:
        lattice_json = json.load(file)
    return lattice_json


def gbkXfrFstLetter(gbk_str: str, style: int) -> str:
    """转换给定的GBK编码字符串。

    参数：
        gbk_str(str)：
            待转换的GBK字符串。
        style(int)：
            三种转换风格，分别为{0=不转换, 1=拼音, 2=拼音首字母}。

    返回：
        转换后的字符串。

    >>> gbkXfrFstLetter('我的祖国', 0)
    '我的祖国'
    >>> gbkXfrFstLetter('我的祖国', 1)
    'wo de zu guo'
    >>> gbkXfrFstLetter('我的祖国', 2)
    'wdzg'
    """
    if style == 0:
        return gbk_str
    elif style == 1:
        pinyin_list = lazy_pinyin(gbk_str)
        pinyin_result = " ".join("".join(inner_list) for inner_list in pinyin_list)
    elif style == 2:
        pinyin_list = pinyin(gbk_str, style=Style.FIRST_LETTER)
        pinyin_result = "".join("".join(inner_list) for inner_list in pinyin_list)
    reg_pinyin_result = re.sub(r"[^a-z\s]", "", pinyin_result)
    return reg_pinyin_result


def extractValues(data: dict, style: int) -> list:
    """从json格式的转写结果提取转写字符进行拼接。

    使用递归对传入的json进行递归遍历，当key为'w'时停止遍历，提取对应的值添加到存储字符的列表。

    参数：
        data(dict):
            downloadOrderResult函数的返回结果的st键值对。
        style(int):
            三种转换风格，分别为{0=不转换, 1=拼音, 2=拼音首字母}。

    返回：
        指定风格的转写结果列表。
    """
    w_values = []
    # 如果data是一个列表，遍历列表中的每个元素，并递归调用extractValues函数，将返回的值扩展到w_values列表中
    if isinstance(data, list):
        for item in data:
            w_values.extend(extractValues(data=item, style=style))
    # 如果data是一个字典，遍历字典中的每个键值对
    elif isinstance(data, dict):
        for key, value in data.items():
            if key == "w":
                w_values.append(gbkXfrFstLetter(value, style=style))
            else:
                w_values.extend(extractValues(data=value, style=style))
    return w_values


# getTransferResult方法：从给定的JSON文件中获取转写结果，并根据需要将中文转换为拼音首字母
def getTransferResult(transfer_json: dict, style: int) -> str:
    """从downloadOrderResult函数的返回结果提取指定风格的转写字符串。

    由于transfer_json参数实际上包含了一个元素为json字符串的列表，每个元素为音频中一句话（歌词），
    因此需要先循环列表每个元素（json_1best)加载为字典，再使用extractValues函数提取每个字典的所有"w"键的值。

    参数：
        transfer_json(dict):
            downloadOrderResult函数的返回结果。
        style(int):
            三种转换风格，分别为{0=不转换, 1=拼音, 2=拼音首字母}。

    返回：
        指定风格的转写结果字符串。
    """
    w_list = []
    for element in transfer_json:
        sentence = json.loads(element["json_1best"])
        w_values = extractValues(sentence, style=style)
        concatenated_string = "".join(w_values)
        w_list.append(concatenated_string)
    transfer_result = "".join(w_list)
    print("\n the transfer result is：\n", transfer_result)
    return transfer_result


def extractLyrics(lyrics_dir: Path, file_name: str, style: int) -> str:
    """从存储歌词的txt提取中文字符后输出指定风格字符串。

    参数：
        lyrics_dir(Path):
            歌词txt文件所在目录的绝对路径。
        file_name(str):
            歌词txt文件名。
        style(int):
            三种转换风格，分别为{0=不转换, 1=拼音, 2=拼音首字母}。

    返回：
        歌词的指定风格字符串。
    """
    lyrics_path = lyrics_dir / file_name
    with open(lyrics_path, "r", encoding="utf-8") as file:
        raw_lyrics = file.read()
    pattern = re.compile(r"[^\u4e00-\u9fa5]")
    lyrics = re.sub(pattern, "", raw_lyrics)
    lyrics = gbkXfrFstLetter(lyrics, style=style)
    return lyrics


def getHotWords(lyrics_dir: Path, file_name: str) -> str:
    """歌词拆分成热词，作为调用API的hotword参数值

    歌词txt文件的标准要求为一行为一句歌词，长度不超过20个中文字符，
    本函数将一个或连续的换行符替换成"|"，并将非中文字符替换为空，从而得到“或”形式的hotword正则表达式。

    参数：
        lyrics_dir(Path):
            歌词txt文件所在目录的绝对路径。
        file_name(str):
            歌词txt文件名。

    返回：
        由|分割的hotword正则表达式字符串。
    """
    lyrics_path = lyrics_dir / file_name
    with open(lyrics_path, "r", encoding="utf-8") as file:
        raw_lyrics = file.read()
    pattern = re.compile(r"[^\u4e00-\u9fa5\n]+")
    result = pattern.sub("", raw_lyrics).replace("\n", "|")
    result = re.sub(r"\|+", "|", result)
    return result


# TODO: 仍然受限于容错率问题，需要考虑使用编辑距离来编写一个新的索引函数。（也可以在findSubstringIndex函数基础上进行改版）
def findSubstringIndex(
    full_str: str, lyrics: str, threshold=0.6, is_end=False, match_str_size=20
) -> int:
    """通过歌词与API转写结果的元素比对确定音频切割在转写结果中的起始索引和终点索引。

    给定API转写结果字符串与歌词字符串，取歌词开头（结尾）前match_str_size个字符作为匹配字符串，
    与API转写结果字符串从开头（结尾）起的前match_str_size个字符串match_str 进行同位元素比对，同位元素个数占比
    如果大于threshold，则返回当前match_str开头（结尾）在API转写结果字符串中的索引，作为开头（结尾）索引，
    否则match_str的起始索引继续往左（右）挪一位，再取match_str_size个字符作为匹配字符串继续匹配。

    注意：保持full_str与lyrics的风格一致！

    参数：
        full_str(str):
            getTransferResult函数的结果字符串。
        lyrics(str):
            歌词字符串。
        threshold(float):
            匹配阈值，当大于此值，则意味着字符串很有可能是同一句话。默认0.6。
        is_end(bool):
            当前任务是否为匹配终点索引。默认False（匹配起始索引）。
        match_str_size(int):
            匹配字符串的长度。默认20。

    返回：
        返回音频切割所需的起始（终点）索引。
    """
    if is_end:
        match_str = lyrics[-1 * match_str_size :]
        range_list = reversed(range(len(full_str) - match_str_size + 1))
    else:
        match_str = lyrics[:match_str_size]
        range_list = range(len(full_str) - match_str_size + 1)
    for i in range_list:
        substring = full_str[i : i + match_str_size]
        match_percentage = (
            sum(1 for x, y in zip(substring, match_str) if x == y) / match_str_size
        )
        if match_percentage >= threshold:
            if is_end:
                return i + match_str_size - 1
            else:
                return i
    raise ValueError(
        f"Failed to match the head index of string {'match_str'}, please try again"
    )


# TODO: 仍然受限于容错率问题，需要考虑使用编辑距离来编写一个新的索引函数。（也可以在findSubstringIndex函数进行改版）
def getCutPoint(lyrics_dir, w_str_result, file_name, threshold, match_str_size=20):
    # lyrics = extractLyrics(
    #     lyrics_dir=lyrics_dir,
    #     file_name=file_name,
    #     style=2)
    # start_cut_point_index = findSubstringIndex(
    #     w_str_result,
    #     is_end=False,
    #     lyrics=lyrics,
    #     match_str_size=match_str_size,
    #     threshold=threshold)
    # end_cut_point_index = findSubstringIndex(
    #     w_str_result,
    #     is_end=True,
    #     lyrics=lyrics,
    #     match_str_size=match_str_size,
    #     threshold=threshold)
    start_cut_point_index = 0
    end_cut_point_index = len(w_str_result) - 1

    print(
        "start_cut_point_index is",
        start_cut_point_index,
        ",end_cut_point_index is",
        end_cut_point_index,
    )
    return start_cut_point_index, end_cut_point_index


def findWbValue(
    sentence: dict, current_index: int, target_index: int, is_end=False
) -> tuple:
    """根据目标索引来确定索引所对应的时间戳。

    遍历传入的sentence的字典，来提取"w"值对应的wb（we）的取值，当加上当前"w"字符串长度后的current_index
    大于等于target_index + 1，返回wb（we），作为音频切割的时间戳。如果遍历完sentence字典current_index仍然
    小于target_index + 1，则返回current_index用作下次调用findWbValue函数的参数。

    参数：
        sentence(dict):
            downloadOrderResult函数的返回结果的st键值对。
        current_index(int):
            当前已积累的索引。
        target_index(int):
            作为切割点的目标索引。由getCutPoint函数计算。
        is_end(bool):
            当前任务是否为匹配终点索引。默认False（匹配起始索引）。

    返回：
        一个元组，包括最新的current_index与对应的wb。
    """
    ws_list = sentence["rt"][0]["ws"]
    for word in ws_list:
        if is_end:
            wb_value = word["we"] * 10
        else:
            wb_value = word["wb"] * 10
        cw_list = word["cw"][0]
        if cw_list["wp"] in ["n", "s"]:
            w_value = gbkXfrFstLetter(word["cw"][0]["w"], style=2)
        else:
            w_value = ""
        current_index += len(w_value)
        if current_index >= target_index + 1:
            break
    return current_index, wb_value


def getCpTimestamp(transfer_json: dict, target_index: int, is_end=False) -> float:
    """遍历API转写结果，找到target_index在音频中对应的时间戳。

    参数：
        transfer_json(dict):
            downloadOrderResult函数的返回结果。
        target_index(int):
            作为切割点的目标索引。由getCutPoint函数计算。
        is_end(bool):
            当前任务是否为匹配终点索引。默认False（匹配起始索引）。

    返回：
        音频切割所需的时间戳，单位为秒。

    """
    current_index = 0
    for element in transfer_json:
        json_best = json.loads(element["json_1best"])
        current_index, wb_values = findWbValue(
            sentence=json_best["st"],
            current_index=current_index,
            target_index=target_index,
            is_end=is_end,
        )
        if current_index >= target_index + 1:
            cut_point_t = int(json_best["st"]["bg"]) + wb_values
            break
    return cut_point_t / 1000


def getPerWordTime(transfer_json: dict) -> list:
    """输出API转写结果json数据的"w"键的值与对应时间戳构成键值对的字典列表。

    参数：
        transfer_json(dict):
            downloadOrderResult函数的返回结果

    返回：
        一个列表，每个元素是一个字典，键为"w"的值，值为时间戳。
    """
    wt_list = []
    for element in transfer_json:
        json_best = json.loads(element["json_1best"])
        sentence_bg = int(json_best["st"]["bg"])
        ws_list = json_best["st"]["rt"][0]["ws"]
        for word in ws_list:
            wb_value = word["wb"] * 10
            w_time = (sentence_bg + wb_value) / 1000
            cw_list = word["cw"][0]
            if cw_list["wp"] in ["n", "s"]:
                w_value = gbkXfrFstLetter(word["cw"][0]["w"], style=0)
                wt_list.append({w_value: w_time})

    return wt_list


def cutAudio(
    start_time=0.0, end_time=None, output_dir=None, output_audio=None, input_audio=None
):
    """给定时间戳对音频进行切割

    参数：
        start_time(float):
            切割的起始时间戳。
        end_time(float):
            切割的终点时间戳。
        output_dir(Path):
            音频文件输出目录的绝对路径。
        output_audio(str):
            音频文件输出名。
        input_audio(Path):
            待切割音频的绝对路径。

    返回：
        已切割的音频文件。

    """
    file_name = os.path.basename(input_audio)
    output_name = file_name + "_" + output_audio
    output_path = output_dir / output_name
    print(f"Start download '{output_path}' ...")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    audio = AudioSegment.from_file(input_audio)
    duration_s = len(audio) / 1000
    if end_time is None:
        end_time = duration_s
    segment = audio[start_time * 1000 : end_time * 1000]
    segment.export(output_path, format="mp3")


if __name__ == "__main__":
    doctest.testmod()
