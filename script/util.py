# -*- coding: utf-8 -*-

"""

这个模块用来存放公用函数

"""

import concurrent.futures
# noinspection PyUnresolvedReferences
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
    """
    定义一个多进程并发执行函数的包装器multipuleProcess，用于将一个函数func_name应用于arg_list中的参数列表，
    并利用最大进程数max_workers进行并行计算，同时支持自定义分块大小chunksize。

    参数：
    - func_name (Callable): 待并行执行的函数。
    - arg_list (list): 函数func_name需要应用的一系列参数列表。
    - max_workers (int, 默认值为逻辑CPU核心数的一半): 最大进程数，用于限制并发执行的进程数量。
    - chunksize (int, 默认值根据arg_list和max_workers动态计算): 分块大小，用于决定每次分配给进程执行的任务数量。

    功能描述：
    1. 根据max_workers创建一个并发.futures.ProcessPoolExecutor上下文管理器。
    2. 如果chunksize参数未指定，则根据arg_list的长度和max_workers自动计算一个合适的分块大小。
    3. 使用executor.map方法将func_name函数并行应用到arg_list的各个元素上，按照设定的chunksize进行分块处理。
    4. 收集所有并行计算结果，将其整合为一个列表并返回。

    返回：
    - result_list (list): 包含所有并行执行结果的列表，其顺序与arg_list中参数的顺序相对应。

    适用于CPU密集型代码
    """
    # 使用with语句创建并发.futures.ProcessPoolExecutor上下文管理器，保证进程池的正确关闭
    with concurrent.futures.ProcessPoolExecutor(max_workers) as executor:
        # 如果chunksize未指定，则根据arg_list的长度和max_workers计算合理的分块大小
        if chunksize is None:
            chunksize = len(arg_list) // max_workers // 20
            # 确保chunksize至少为1，避免无法进行有效的任务分割
            if chunksize <= 1:
                chunksize = 1

        # 使用executor.map函数将func_name并行应用到arg_list的每个元素上，分块大小为chunksize
        result_list = list(executor.map(func_name, arg_list, chunksize=chunksize))

    return result_list


def multipuleThread(
    func_name=None,
    arg_list: list = None,
    max_workers: int = psutil.cpu_count(logical=True),
):
    """
    定义一个名为multipuleThread的函数，该函数旨在并发地执行用户提供的函数func_name，并将结果收集到一个列表中。
    通过线程池并发处理，提高了执行效率，充分利用多核CPU资源。

    参数：
    - func_name (Callable, 默认None): 需要并发执行的函数对象。
    - arg_list (list, 默认None): 包含多个参数的列表，这些参数将分别传递给func_name函数执行。
    - max_workers (int, 默认psutil.cpu_count(logical=True)): 线程池中最大线程数量，默认为逻辑处理器核心数。

    返回：
    - result_list (list): 包含func_name函数执行完毕后所有结果的列表，其顺序与arg_list中的参数顺序一致。

    适用于I/O密集型代码
    """
    # 使用with语句创建一个线程池Executor上下文管理器，根据max_workers参数初始化线程池大小
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 使用map方法将func_name函数并行地应用到arg_list的每个元素上，并将结果收集到result_list中
        result_list = list(executor.map(func_name, arg_list))

    return result_list


def writeCsv(write_dict_list: list, csv_dir: Path, csv_name: str, overwrite: bool = False):
    """
    将数据字典列表写入或追加、覆写到CSV文件中。

    参数：
    - write_dict_list (list): 包含多个字典的列表，每个字典的键作为CSV列名，值作为列内容。
    - csv_dir (Path): CSV文件所在的目录路径对象。
    - csv_name (str): CSV文件的名称。
    - overwrite (bool, 默认为False): 如果为True，则覆写（覆盖）现有的CSV文件；否则在原有文件基础上追加数据。

    功能描述：
    此函数首先根据write_dict_list的第一个字典获取所有的字段名（即CSV列名），
    然后根据csv_dir和csv_name构造目标CSV文件的完整路径。
    当指定的CSV文件不存在时，新建并写入表头和所有数据；
    若文件已存在且overwrite为True，则删除原有文件并重新写入所有数据；
    若文件已存在且overwrite为False，则在原有文件末尾追加数据。

    返回：
    无，但会在控制台输出CSV文件的创建或更新状态。
    """

    fieldnames = write_dict_list[0].keys()
    csv_file_path = csv_dir / csv_name

    if overwrite and os.path.exists(csv_file_path):
        # 如果overwrite为True且文件存在，则先删除原有的CSV文件
        os.remove(csv_file_path)

    mode = "a" if os.path.exists(csv_file_path) else "w"
    with open(csv_file_path, mode=mode, newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(fieldnames))

        # 对于新创建的文件，总是写入表头
        if mode == "w":
            writer.writeheader()

        # 写入或追加数据行
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
        pattern = re.compile(r'[^\u4e00-\u9fa5]')
        return pattern.sub('', gbk_str)
    elif style == 1:
        pinyin_list = lazy_pinyin(gbk_str)
        pinyin_result = " ".join("".join(inner_list) for inner_list in pinyin_list)
    elif style == 2:
        pinyin_list = pinyin(gbk_str, style=Style.FIRST_LETTER)
        pinyin_result = "".join("".join(inner_list) for inner_list in pinyin_list)
    reg_pinyin_result = re.sub(r"[^a-z\s]", "", pinyin_result)
    return reg_pinyin_result