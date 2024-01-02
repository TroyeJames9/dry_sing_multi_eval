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


def formGraph(audio_file):
    y, sr = librosa.load(audio_file)

    # 计算onset envelope
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)

    # 使用tempo和beat_frames识别节拍
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)

    # 绘制音频波形和节拍
    plt.figure(figsize=(20, 15))

    # 音频波形
    plt.subplot(4, 3, 1)
    librosa.display.waveshow(y, sr=sr, alpha=0.5)
    plt.vlines(librosa.frames_to_time(beat_frames), -1, 1, color='r', linestyle='--', label='Beats')
    plt.title(f'Beat Detection at {tempo:.2f} BPM')
    plt.legend()

    # 绘制谱图
    plt.subplot(4, 3, 2)
    spectrogram = librosa.stft(y)
    spectrogram_db = librosa.amplitude_to_db(np.abs(spectrogram))
    librosa.display.specshow(spectrogram_db, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')

    # 梅尔频谱图
    plt.subplot(4, 3, 4)
    S = librosa.feature.melspectrogram(y=y, sr=sr)
    S_dB = librosa.power_to_db(S, ref=np.max)
    librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel')
    plt.title('Mel Spectrogram')

    # 频率-时间图
    plt.subplot(4, 3, 5)
    plt.specgram(y, NFFT=2048, Fs=2, Fc=0, noverlap=128, cmap='viridis', sides='default', mode='default', scale='dB');
    plt.title('Frequency-Time Plot')

    # 光谱包络图
    plt.subplot(4, 3, 6)
    tempogram = librosa.feature.tempogram(y=y, sr=sr)
    librosa.display.specshow(tempogram, sr=sr, x_axis='time', y_axis='tempo')
    plt.title('Tempogram')

    plt.tight_layout()
    plt.show()


# 使用方法
formGraph(audio_file=audio_file)

