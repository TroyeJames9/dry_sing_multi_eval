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

'''resultPictueres()创建相关存储文件夹，首先如果有resultPictueres则跳到下一步，如果没有则创建文件夹；
然后继续创建存储各种类型图片的文件夹'''


def resultPictueres():
    picture = ["CQT图", "Waveform 波形图", "Spectrogram 谱像", "Mel Spectrogram 梅尔频谱图",
               "Frequency-Time Plot 频率-时间图", "Spectral Envelope 光谱包络图"]
    download_dir = ROOT / 'resultPictures'

    # 判断存储图片结果的文件夹resultPictueres是否已经存在，若已存在则不执行下载操作

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        print(f"Path '{download_dir}' created.")
    else:
        print(f"Path '{download_dir}' already exists.")

    # 创建一个字典，将每个元素与下载目录拼接成新路径
    new_download_dir = {name: download_dir / name for name in picture}

    # 创建文件夹
    for name, path in new_download_dir.items():
        # 检查下载目录是否存在，如果不存在则创建该目录
        os.makedirs(path, exist_ok=True)


# audio_folder为音频文件夹路径，output_folder为输出CQT图像的文件夹路径
def CQT(audio_folder=ROOT / "audio/qilai", output_folder=ROOT / 'resultPictures/CQT图'):
    # 获取音频文件夹中的所有文件夹名
    subfolders = os.listdir(audio_folder)
    print(subfolders)
    # 循环处理每个音频文件夹
    for subfolder in subfolders:
        audio_path = os.path.join(audio_folder, subfolder)

        # 使用Librosa加载音频
        y, sr = librosa.load(audio_path)

        # 生成CQT图
        C = librosa.amplitude_to_db(np.abs(librosa.cqt(y, sr=sr)), ref=np.max)

        # 创建输出图像文件名
        output_filename = os.path.splitext(subfolder)[0] + '.png'
        output_path = os.path.join(output_folder, output_filename)

        # 保存CQT图为图像文件
        plt.figure(figsize=(8, 8))
        plt.axis('off')
        plt.imshow(C, cmap='viridis', origin='lower', aspect='auto')
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0, transparent=False)
        plt.close()

        print(f'Converted {subfolder} to {output_filename}')

    print('Conversion complete.')


'''对音频格式的文件使用Matplotlib库来绘制常见的五种音频图'''


def formGraph(audio_file):
    y, sr = librosa.load(audio_file)

    # 计算onset envelope
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)

    # 使用tempo和beat_frames识别节拍
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)

    # 绘制音频波形和节拍
    plt.figure(figsize=(20, 15))

    # 绘制谱图
    plt.subplot(4, 3, 2)
    spectrogram = librosa.stft(y)
    spectrogram_db = librosa.amplitude_to_db(np.abs(spectrogram))
    librosa.display.specshow(spectrogram_db, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')

    # 音频波形
    plt.subplot(4, 3, 1)
    librosa.display.waveshow(y, sr=sr, alpha=0.5)
    plt.vlines(librosa.frames_to_time(beat_frames), -1, 1, color='r', linestyle='--', label='Beats')
    plt.title(f'Beat Detection at {tempo:.2f} BPM')
    plt.legend()

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


def run():
    resultPictueres()
    CQT()
    # 读取音 频文件
    audio_file = ROOT / "audio/song_demo.mp3"  # 替换为你的音频文件路径
    formGraph(audio_file=audio_file)


if __name__ == '__main__':
    run()
