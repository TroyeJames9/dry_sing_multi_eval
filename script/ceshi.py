import librosa
import librosa.display
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import os
import librosa.display
import numpy as np
import aubio
from articulation_analysis import calculate_cosine_similarity

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # program root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

# 读取音 频文件
audio_file = ROOT / "audio/song_demo.mp3"  # 替换为你的音频文件路径
audio_file_1 = ROOT / "audio/qilai_wav/qilai.wav"
audio_file_2 = ROOT / "audio/qilai_wav/qilai_1.wav"
audio_file_3 = ROOT / "audio/qilai/qilai.mp3"

'''尝试使用aubio库识别音高、节拍'''


def analyze_audio(filename):
    # 加载音频文件
    samplerate, audio = aubio.source(filename)

    # 创建音高识别对象
    pitch_o = aubio.pitch("yin", samplerate)
    pitch_o.set_unit("Hz")
    pitch_o.set_tolerance(0.8)

    # 创建节拍识别对象
    tempo_o = aubio.tempo("default", win_s=512, hop_s=256, samplerate=samplerate)

    # 分析音频
    pitches = []
    beats = []

    while True:
        samples, read = audio()

        # 音高分析
        pitch = pitch_o(samples)[0]
        confidence = pitch_o.get_confidence()
        if confidence > 0.8:
            pitches.append(pitch)

        # 节拍分析
        is_beat = tempo_o(samples)[0]
        if is_beat:
            beats.append(is_beat)

        if read < len(samples):
            break

    return pitches, beats


'''使用librosa函数返回函数的音高，将音高值转为MIDI值，然后绘制成折线图'''


def analyze_pitch(audio_file):
    # 读取音频文件
    y, sr = librosa.load(audio_file)

    # 计算音频的音高
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)

    # 获取音高的索引
    pitch_index = pitches.argmax(axis=0)

    # 将索引映射为音高频率
    pitch_frequencies = librosa.core.midi_to_hz(pitch_index)

    # 将频率转换为 MIDI
    pitch_midi = librosa.core.hz_to_midi(pitch_frequencies)

    # 绘制音高曲线（折线图）
    plt.figure(figsize=(14, 5))
    times = librosa.times_like(pitches)
    plt.plot(times, pitch_midi, color='r', label='Pitch (MIDI)')
    plt.title('Pitch Analysis')
    plt.xlabel('Time (s)')
    plt.ylabel('Pitch (MIDI)')
    plt.legend()
    plt.show()
    return pitch_midi


# 使用示例

# a = analyze_pitch(audio_file_1)
# print(a)

'''使用audio进行音高检测，我们创建了一个aubio.pitch对象，并使用"yin"算法进行音高检测。
然后，我们打开音频文件，并在一个循环中逐帧读取音频数据，并通过aubio.pitch对象计算当前帧的音高。
如果检测到非零音高值，我们将其转换为MIDI音高编号，并将其添加到midi_pitches列表中'''


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
# plt.plot(midi_standard, label='aubio')
# plt.plot(a, label='librosa')
# # 添加图例
# plt.legend()
# # 显示图表
# plt.show()
# print(f"标准是{midi_standard}")
# print(f"测试是{midi_train}")


'''使用Matplotlib库来实现两首歌的音高差异，绘制差异曲线和直方图'''


def plot_pitch_difference(midi_standard, midi_train):
    # 计算音高差异
    pitch_difference = np.array(midi_standard) - np.array(midi_train)

    # 绘制差异曲线
    plt.figure(figsize=(10, 4))
    plt.plot(pitch_difference, color='blue')
    plt.xlabel('帧数')
    plt.ylabel('音高差异')
    plt.title('音高差异曲线')
    plt.show()

    # 绘制差异直方图
    plt.figure(figsize=(8, 6))
    plt.hist(pitch_difference, bins=20, color='green', edgecolor='black')
    plt.xlabel('音高差异')
    plt.ylabel('频数')
    plt.title('音高差异直方图')
    plt.show()


# 假设你已经提取了两首歌的音高并存储在midi_pitches1和midi_pitches2中
# plot_pitch_difference(midi_standard, midi_train)

'''节拍识别'''

audio_file_1 = librosa.load(audio_file)
y, sr = audio_file_1
# 计算每分钟的节拍次数 BPM
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
print(' tempo: {:.2f} beats per minute'.format(tempo))
# 分析音频信号并找出可能的节拍位置，这些位置以帧的形式表示，每个帧都对应音频信号中的一个特定时间点
beat_times = librosa.frames_to_time(beat_frames, sr=sr)
print(beat_times)

contrast_time = []
for i in range(1, len(beat_times)):
    time = beat_times[i] - beat_times[i - 1]
    contrast_time.append(time)
print(f'每节拍之间的时间差{contrast_time}')

