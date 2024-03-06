# -*- coding: utf-8 -*-
import concurrent.futures
import multiprocessing
import psutil
import csv
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
