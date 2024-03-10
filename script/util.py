# -*- coding: utf-8 -*-
import concurrent.futures
import multiprocessing
import psutil
import csv
from pypinyin import pinyin, lazy_pinyin, Style
from setting import *


def multipuleProcess(
    func_name=None,
    arg_list: list = None,
    max_workers: int = psutil.cpu_count(logical=False) // 2,
    chunksize: int = None
):
    with concurrent.futures.ProcessPoolExecutor(max_workers) as executor:
        if chunksize is None:
            chunksize = len(arg_list) // max_workers // 20
            if chunksize <= 1:
                chunksize = 1
        result_list = list(executor.map(func_name, arg_list, chunksize=chunksize))

    return result_list


def writeCsv(write_dict_list: list, csv_dir: Path, csv_name: str):
    fieldnames = write_dict_list[0].keys()
    csv_file_path = csv_dir / csv_name
    if not os.path.isfile(csv_file_path):
        with open(csv_file_path, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(fieldnames))
            writer.writeheader()
            writer.writerows(write_dict_list)
    else:
        # 如果文件已存在，则以追加模式打开
        with open(csv_file_path, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(fieldnames))
            writer.writerows(write_dict_list)

    print("CSV文件已创建或更新：", csv_file_path)


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
