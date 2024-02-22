# -*- coding: utf-8 -*-

"""本模块根据整体框架设计而对data文件夹的数据进行合并、计算，最终得到指标结果表

"""
import pandas as pd
from pathlib import Path


def batchCsv2Pd(csv_dir, encoding='ANSI'):
    """
    批量读取指定路径下的CSV文件，并返回一个字典。
    参数：
    param csv_dir: 文件的绝对路径，Path对象
    返回
    csv_d:键名为文件名（不包括扩展名），值为对应的pd.DataFrame
    """
    csv_d = {}  # 初始化结果字典
    for csv_file in csv_dir.glob('*.csv'):  # 遍历目录下的所有CSV文件
        df = pd.read_csv(csv_file, encoding=encoding)  # 读取CSV文件为DataFrame
        file_name = csv_file.stem  # 获取文件名（不包括扩展名）
        csv_d[file_name] = df  # 将DataFrame存储在字典中，键为文件名
    return csv_d
