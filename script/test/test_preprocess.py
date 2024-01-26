# -*- coding: utf-8 -*-
import unittest
import numpy as np
import librosa
from setting import *
from preprocess.prep_audio import *


class TestPrepAudio(unittest.TestCase):
    def setUp(self) -> None:
        self.audio_dir = UPLOAD_FILE_DIR
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


if __name__ == "__main__":
    unittest.main()
