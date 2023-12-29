import librosa
import librosa.display
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import os

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # program root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative


# 读取音频文件
audio_file =ROOT / "audio/song_demo.mp3"  # 替换为你的音频文件路径
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
