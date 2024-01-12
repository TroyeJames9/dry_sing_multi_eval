import librosa
import librosa.display
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import os
import librosa.display
import numpy as np
import aubio

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # program root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

'''使用audio进行音高检测，我们创建了一个aubio.pitch对象，并使用"yin"算法进行音高检测。
然后，我们打开音频文件，并在一个循环中逐帧读取音频数据，并通过aubio.pitch对象计算当前帧的音高。
如果检测到非零音高值，我们将其转换为MIDI音高编号，并将其添加到midi_pitches列表中'''


# 音高检测
def extract_midi_pitches(filename, samplerate=44100, hop_size=512, win_size=4096):
    # 创建 pitch 对象
    pitch_o = aubio.pitch("yin", win_size, hop_size, samplerate)
    pitch_o.set_tolerance(0.8)

    # 打开音频文件
    source = aubio.source(filename, samplerate, hop_size)
    total_frames = 0
    midi_pitches = []

    while True:
        # 读取音频数据
        samples, read = source()

        # 计算当前帧的音高
        pitch = pitch_o(samples)[0]

        # 如果检测到音高
        if pitch != 0:
            # 将音高转换为 MIDI 编号
            midi_pitch = int(round(aubio.freqtomidi(pitch)))
            midi_pitches.append(midi_pitch)

        total_frames += read

        # 如果没有读取到数据，则退出循环
        if read < hop_size:
            break

    return midi_pitches

# midi_standard = extract_midi_pitches(str(audio_file_1))
# midi_train = extract_midi_pitches(str(audio_file_2))
# print(f"标准是{midi_standard}")
# print(f"测试是{midi_train}")
