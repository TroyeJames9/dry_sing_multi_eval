# -*- coding: utf-8 -*-
import unittest
from setting import *
from result import *


class TestResult(unittest.TestCase):
    def setUp(self) -> None:
        self.csv_dir = TEST_RAWDATA_DIR
        self.expected_pd_dict_keys = ["文件歌曲表", "文件评分表", "模型结果表", "调号音符频率表"]

    def test_batchCsv2Pd(self):
        pd_dict = batchCsv2Pd(csv_dir=self.csv_dir)
        assertEqual(set(pd_dict.keys()) == set(self.expected_pd_dict_keys))
