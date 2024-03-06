# -*- coding: utf-8 -*-
import concurrent.futures
import multiprocessing
import psutil
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
