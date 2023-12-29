import librosa
import librosa.display
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import os
import librosa.display
import numpy as np

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # program root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

# 读取音 频文件
audio_file = ROOT / "audio/song_demo.mp3"  # 替换为你的音频文件路径


# def formGraph(audio_file):
#     y, sr = librosa.load(audio_file)
#
#     # 计算onset envelope
#     onset_env = librosa.onset.onset_strength(y=y, sr=sr)
#
#     # 使用tempo和beat_frames识别节拍
#     tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
#
#     # 绘制音频波形和节拍
#     plt.figure(figsize=(20, 15))
#
#     # 音频波形
#     plt.subplot(4, 3, 1)
#     librosa.display.waveshow(y, sr=sr, alpha=0.5)
#     plt.vlines(librosa.frames_to_time(beat_frames), -1, 1, color='r', linestyle='--', label='Beats')
#     plt.title(f'Beat Detection at {tempo:.2f} BPM')
#     plt.legend()
#
#     # 谱图
#     plt.subplot(4, 3, 2)
#     D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
#     librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
#     plt.title('Spectrogram')
#
#     # 梅尔频谱图
#     plt.subplot(4, 3, 3)
#     S = librosa.feature.melspectrogram(y=y, sr=sr)
#     S_dB = librosa.power_to_db(S, ref=np.max)
#     librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel')
#     plt.title('Mel Spectrogram')
#
#     # 色彩图
#     plt.subplot(4, 3, 4)
#     librosa.display.specshow(D, cmap='viridis', sr=sr, x_axis='time', y_axis='log')
#     plt.title('Spectrogram with Colormap')
#
#     # 频率-时间图
#     plt.subplot(4, 3, 5)
#     plt.specgram(y, NFFT=2048, Fs=2, Fc=0, noverlap=128, cmap='viridis', sides='default', mode='default', scale='dB');
#     plt.title('Frequency-Time Plot')
#
#     # 光谱包络图
#     plt.subplot(4, 3, 6)
#     tempogram = librosa.feature.tempogram(y=y, sr=sr)
#     librosa.display.specshow(tempogram, sr=sr, x_axis='time', y_axis='tempo')
#     plt.title('Tempogram')
#
#     plt.tight_layout()
#     plt.show()


# 使用方法
# formGraph(audio_file=audio_file)

# 绘制音频的谱图
# audio_file = "/Users/lijianxin/speech_recognition/audio/song_demo.mp3"
# audio, sr = librosa.load(audio_file, sr=None)
#
# spectrogram = librosa.stft(audio)
# spectrogram_db = librosa.amplitude_to_db(abs(spectrogram))
#
# plt.figure(figsize=(10, 4))
# librosa.display.specshow(spectrogram_db, sr=sr, x_axis='time', y_axis='log')
# plt.colorbar(format='%+2.0f dB')
# plt.title('Spectrogram')
# plt.show()


# # 替换为你的音频文件路径
# audio_file = "/Users/lijianxin/speech_recognition/audio/music.mp3"
#
# # 载入音频文件
# y, sr = librosa.load(audio_file)
#
# # 提取节拍信息
# tempo, beat_frames = librosa.beat.beat_track(y, sr=sr)
#
# # 将帧索引转换为时间
# beat_times = librosa.frames_to_time(beat_frames, sr=sr)
#
# # 绘制音频波形和节拍
# plt.figure(figsize=(14, 5))
# librosa.display.waveshow(y, sr=sr, alpha=0.5)
# plt.vlines(beat_times, -1, 1, color='r', linestyle='--', label='Beats')
# plt.title('Waveform with Beats')
# plt.xlabel('Time (s)')
# plt.ylabel('Amplitude')
# plt.legend()
# plt.show()
#
# # 根据节拍切割音频
# for i in range(len(beat_times) - 1):
#     start_time = beat_times[i]
#     end_time = beat_times[i + 1]
#     segment = y[int(start_time * sr):int(end_time * sr)]
#
#     # 处理每个切割的音频段，可以保存到文件或进行其他处理
#     # 例如，保存到文件： librosa.output.write_wav(f"segment_{i}.wav", segment, sr)


def plot(audio_file):
    # 加载音频文件
    y, sr = librosa.load(audio_file)

    # 计算onset envelope
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)

    # 使用tempo和beat_frames识别节拍
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)

    # 绘制音频波形和节拍
    plt.figure(figsize=(14, 5))
    librosa.display.waveshow(y, sr=sr, alpha=0.5)
    plt.vlines(librosa.frames_to_time(beat_frames), -1, 1, color='r', linestyle='--', label='Beats')
    plt.title(f'Beat Detection at {tempo:.2f} BPM')
    plt.legend()
    plt.show()

    # 绘制谱图
    spectrogram = librosa.stft(y)
    spectrogram_db = librosa.amplitude_to_db(np.abs(spectrogram))

    plt.figure(figsize=(10, 4))
    librosa.display.specshow(spectrogram_db, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.show()

    # 梅尔频谱图
    plt.subplot(4, 3, 3)
    S = librosa.feature.melspectrogram(y=y, sr=sr)
    S_dB = librosa.power_to_db(S, ref=np.max)
    librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel')
    plt.title('Mel Spectrogram')
    plt.show()

    # 色彩图
    plt.subplot(4, 3, 4)
    librosa.display.specshow(D, cmap='viridis', sr=sr, x_axis='time', y_axis='log')
    plt.title('Spectrogram with Colormap')
    plt.show()



# 使用方法

plot(audio_file=audio_file)
