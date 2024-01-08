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


def run():
    resultPictueres()
    CQT()


if __name__ == '__main__':
    run()
