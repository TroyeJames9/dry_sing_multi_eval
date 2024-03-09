import pandas as pd
from pathlib import Path
import re
import logging
import glob
from setting import *

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format="%(message)s")


def audioSampling(
    csv_dir=RAW_DATA_DIR, csv_name=SONGNAME_CSV, song_names: list = None, max_samples=5
):
    """
    从CSV文件中提取指定曲目、指定数量的音频数据行，并将其保存为pd.DataFrame。

    参数：
    - csv_dir: 包含音频数据的CSV文件所在目录的绝对路径，默认为RAW_DATA_DIR
    - csv_name: 包含音频数据的CSV文件名称，默认为SONGNAME_CSV
    - song_names: 用于匹配曲目名称的正则表达式列表，默认为['guoge', '茉莉花']
    - max_samples: 每个曲目最大抽取的数据行数，默认为5

    返回：
    - pd.DataFrame 包含提取的音频数据
    """
    # 构建CSV文件路径
    csv_file_path = csv_dir / csv_name

    # 读取CSV文件，指定编码方式
    df = pd.read_csv(csv_file_path, encoding="ANSI", engine="python")

    # 使用正则表达式结合两个歌曲名称进行匹配
    combined_regex = "|".join(song_names)
    selected_rows = df[df["歌曲名"].str.contains(combined_regex, case=False, na=False)]

    # 限制每个曲目的抽取数量
    selected_rows["抽取数量"] = selected_rows.groupby("歌曲名").cumcount() + 1
    selected_rows = selected_rows[selected_rows["抽取数量"] <= max_samples]

    logging.info("提取的音频数据：\n%s", selected_rows.drop(columns="抽取数量"))
    return selected_rows.drop(columns="抽取数量")


def catSampling(result_df):
    """
    将audioSampling的结果进行分类，分类结果返回一个字典

    参数：
    - result_df: audioSampling 函数的结果，包含 '文件名' 和 '歌曲名' 列
    - song_dict: 存储函数结果的字典
    返回：
    - song_dict: 返回一个字典，'歌曲名'为键，'文件名列表'为值
    """
    # 如果 result_df 为 None，直接返回空字典
    if result_df is None or result_df.empty:
        return {}
    # 初始化字典
    song_dict = {}

    # 遍历结果数据框的每一行
    for index, row in result_df.iterrows():
        song_name = row["歌曲名"]
        file_name = row["mp3文件名"]

        # 如果歌曲名称不在字典中，添加新的键值对
        if song_name not in song_dict:
            song_dict[song_name] = [file_name]
        else:
            # 如果歌曲名称已存在，将文件名添加到对应的列表中
            song_dict[song_name].append(file_name)
    # 日志记录结果
    for song_name, file_names in song_dict.items():
        logging.info(f"{song_name}: {file_names}\n")
    # 返回字典
    return song_dict


def tempCatSampling(input_audio_dataset: str):
    """由于切割算法未竣工，暂时获取已切割好的705首国歌来直接照搬catSampling的输出格式"""
    sampling_dict = {}
    folder_path = UPLOAD_FILE_DIR / input_audio_dataset

    # sampling_dict["guoge"] = glob.glob(os.path.join(folder_path, "*.wav"))
    sampling_dict[input_audio_dataset] = [
        os.path.abspath(os.path.join(folder_path, filename))
        for filename in os.listdir(folder_path)
        if filename.endswith('.mp3')
    ]

    return sampling_dict


def getScpFile(sampling_dict: dict, scp_dir: Path = SCP_DATA_DIR):
    for song_name in sampling_dict.keys():
        files_list = sampling_dict[song_name]
        scp_dict = {}
        for file_path in files_list:
            file_name = os.path.basename(file_path)
            file_name = re.sub(r'\..*', '', file_name)
            scp_dict[file_name] = file_path

        scp_name = song_name + ".scp"
        scp_path = scp_dir / scp_name
        if os.path.exists(scp_path):
            # 如果文件存在，则清空文件内容
            open(scp_path, 'w').close()
        with open(scp_path, 'w') as f:
            for key, value in scp_dict.items():
                value = value.replace("\\", "/")
                f.write(f"{key} {value}\n")

    return scp_dict


if __name__ == "__main__":
    sampling_dict = tempCatSampling("qilai")
    getScpFile(sampling_dict)
