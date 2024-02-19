# -*- coding: utf-8 -*-
import unittest
import numpy as np
import librosa
from setting import *
from preprocess.prep_audio import *
from preprocess.prep_notation import *
from preprocess.lfasr_new import *


class TestPrepExtract(unittest.TestCase):
    def setUp(self) -> None:
        self.raw_data_dir = 'E:/PythonCode/Project2/data/raw_data'
        self.freq_csv = '文件歌曲表.csv'
        csv_path = Path(self.raw_data_dir) / self.freq_csv
        self.sample_df = pd.read_csv(csv_path, encoding='ANSI', engine='python')

    def test_audioSampling(self):
        result_df = audioSampling(song_names=['茉', '歌', '粉'], max_samples=4)
        # 在这里添加你的测试断言
        self.assertEqual(len(result_df), 12)  # 检查是否返回了正确数量的行
        self.assertTrue(all(result_df['歌曲名'].str.contains('茉|歌|粉', case=False)))  # 检查歌曲名称是否与给定的正则表达式匹配
        self.assertTrue(all(result_df.groupby('歌曲名')['mp3文件名'].count() <= 10))  # 检查是否满足max_samples条件

    def test_catSampling(self):
        song_dict = catSampling(result_df)
        # 测试断言
        self.assertIn('国歌', song_dict)  # 检查 '国歌' 是否在返回的字典中
        self.assertIsInstance(song_dict['国歌'], list)  # 检查 '国歌' 对应的值是否是列表类型
        self.assertGreater(len(song_dict['国歌']), 0)  # 检查 '国歌' 对应的值列表是否非空
        self.assertIn('茉莉花', song_dict)  # 检查 '茉莉花' 是否在返回的字典中


class TestPrepNotation(unittest.TestCase):
    def setUp(self) -> None:
        self.json_dir = TEST_EIGEN_DIR
        self.raw_data_dir = TEST_RAWDATA_DIR
        self.json_name = "中华人民共和国国歌测试"
        self.json_time_name = "中华人民共和国国歌_时间结果"
        self.json_freq_name = "中华人民共和国国歌_最终结果"
        self.freq_csv = FREQ_CSV

        self.notation_dict = extractJson(
            json_dir=self.json_dir, json_name=self.json_name
        )
        self.notation_dict_time = extractJson(
            json_dir=self.json_dir, json_name=self.json_time_name
        )
        self.notation_dict_freq = extractJson(
            json_dir=self.json_dir, json_name=self.json_freq_name
        )

        self.note_sig = "G"

    def test_extractJson(self):
        n_dict = extractJson(json_dir=self.json_dir, json_name=self.json_name)
        self.assertIsNotNone(n_dict)

    def test_calNoteTime(self):
        t_dict = calNoteTime(eigen_dict=self.notation_dict)
        # 节拍时间转化结果是否符合预期
        self.assertDictEqual(t_dict, self.notation_dict_time)

    def test_calNoteFreq(self):
        f_dict = calNoteFreq(
            eigen_dict_t=self.notation_dict_time,
            data_dir=self.raw_data_dir,
            data_name=FREQ_CSV,
            note_sig=self.note_sig,
        )
        # 音符频率转化结果是否符合预期
        self.assertDictEqual(f_dict, self.notation_dict_freq)


class TestPrepAudio(unittest.TestCase):
    def setUp(self) -> None:
        self.audio_dir = TEST_AUDIO_DIR
        self.dataset_name = "qilai"
        self.audio_name = "qilai_1.mp3"
        self.target_sr = 16000

        self.vt_audio = None
        self.vt_sr = None

    def test_PrepAudio(self):
        self.vt_audio, self.vt_sr = xfrVocalTract(
            audio_dir=self.audio_dir,
            dataset_name=self.dataset_name,
            audio_name=self.audio_name,
            target_sr=self.target_sr,
        )
        duration_seconds = librosa.get_duration(y=self.vt_audio, sr=self.vt_sr)
        # 重采样结果是否正确
        self.assertEqual(len(self.vt_audio), self.target_sr * duration_seconds)
        # 结果是否为单声道
        self.assertEqual(len(self.vt_audio.shape), 1)
        rs_y = noiseReduce(y=self.vt_audio, sr=self.vt_sr)
        # 降噪是否生效(频域能量是否变化)
        self.assertNotEqual(np.sum(rs_y), np.sum(self.vt_audio))


class TestLfasrNew(unittest.TestCase):
    def setUp(self) -> None:
        self.json_dir = TEST_RESULT_DIR
        self.test_json_name = "orderResult_lattice.json"
        self.result_json_name = "getWordInfoList_result.json"

        self.test_dict = extractJson(
            json_dir=self.json_dir, json_name=self.test_json_name
        )
        self.result_dict = extractJson(
            json_dir=self.json_dir, json_name=self.result_json_name
        )

    def test_getWordInfoList(self):
        eigen_list = getWordInfoList(transfer_json=test_dict)
        self.assertDictEqual(eigen_list, self.result_dict)


if __name__ == "__main__":
    unittest.main()
