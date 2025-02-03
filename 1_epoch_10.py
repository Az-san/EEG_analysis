#######################################################################################################
#  2024/12/23 作成
#  2025/01/15 改訂
#  2025/02/03 再改訂（波形プロット部削除）
#
#  --1024Hzデータ用, 2-10Hzフィルタ版--
#  【0_before_10.py の後に実行すること】
#
# 【概要】エポック切り出しと波形プロット（2-10Hzフィルタ版）
# 生データ（raw_data.csv）と、0_before_10.py で前処理されたICA処理済みデータ（2-10Hz_1ms.csv）を読み込み、
# TTL信号を基準にエポックを切り出す。各電極のエポックデータをCSV形式で保存し、波形プロットを作成する。
# オリジナル波形（-1000ms～+2000ms）とズームイン波形（-500ms～+500ms）を出力する。
#
# 【処理内容】
# 1. 生データ（raw_data.csv）と前処理済みICAデータ（2-10Hz_1ms.csv）をGUIで選択
# 2. TTL信号（生データ9列目）に基づき、-1〜+2秒のエポックデータを切り出す
# 3. 各電極ごとにエポックデータを "calc/epoch/original" と "calc/epoch/zoomed" にPNG形式で保存
# 4. 切り出したデータを統合し、"calc/epoch_summary" にCSV形式で保存
#
# 【出力先】
# - 統合CSV: "calc/epoch_summary/{電極名}_epoch_summary.csv"
#
# 【注意事項】
# - 生データ: CSV形式（"windows-1252"エンコーディング）
# - ICAデータ: 0_before_10.py で作成された "2-10Hz_1ms.csv" を使用
# - TTL信号が -1000ms 〜 +2000ms の範囲内に収まることを確認すること
# - 必ず前処理済みデータ（0_before_10.py 実行後のデータ）を使用すること
#######################################################################################################


import pandas as pd
import numpy as np
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory
from datetime import datetime

start_time = datetime.now()
print(f"プログラム開始時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

# GUIを使ったディレクトリ選択関数
def select_directory(prompt):
    print(prompt)
    Tk().withdraw()
    return askdirectory(title=prompt)

# GUIを使ったファイル選択関数
def select_file(prompt):
    print(prompt)
    Tk().withdraw()
    return askopenfilename(title=prompt)

# 解析のルートディレクトリをユーザーに選択させる
root_dir = select_directory("解析のルートディレクトリを選択してください")
calc_dir = os.path.join(root_dir, "calc")
summary_output_dir = os.path.join(calc_dir, "epoch_summary")
os.makedirs(summary_output_dir, exist_ok=True)

# 生データ（CSV）とICA処理済みデータのファイルを選択
raw_data_file = select_file("生データ（.csv）のファイルを選択してください。")
ica_data_file = select_file("ICA処理済みデータ（2-10Hz_1ms.csv）のファイルを選択してください。")

# データの読み込み
try:
    raw_data = pd.read_csv(raw_data_file, encoding='windows-1252')
    ica_data = pd.read_csv(ica_data_file)
except Exception as e:
    print(f"データ読み込み中にエラーが発生しました: {e}")
    raise

# 電極リスト
electrodes = ["F3", "Fz", "F4", "FCz", "Cz"]

# 時間データの取得
try:
    time_data = np.round(ica_data.iloc[:, 0].values * 1000, decimals=6)  # Time列の取得と丸め
except Exception as e:
    print(f"時間データの取得中にエラーが発生しました: {e}")
    raise

# TTL信号の取得
ttl_times = np.round(raw_data.iloc[5:61, 9].values * 1000, decimals=6)  # TTL信号を[s]から[ms]に変換して丸め

# 各TTL信号のタイミングを最も近い値で一致判定
valid_ttl_times = []
for ttl in ttl_times:
    closest_idx = np.searchsorted(time_data, ttl)
    if closest_idx < len(time_data) and abs(time_data[closest_idx] - ttl) < 1:
        valid_ttl_times.append(time_data[closest_idx])
print(f"有効なTTL信号の数: {len(valid_ttl_times)}")

# エポック範囲とサンプリング設定
epoch_start = -1000
epoch_end = 2000
num_samples = epoch_end - epoch_start

# 各電極の統合データを保持する辞書
epoch_summary_data = {electrode: [] for electrode in electrodes}

# 各電極ごとにエポック切り出し処理
for electrode in electrodes:
    electrode_data = ica_data[electrode].values
    epoch_time = np.arange(epoch_start, epoch_end)  # Time列の生成

    for ttl in valid_ttl_times:
        try:
            ttl_idx = np.abs(time_data - ttl).argmin()
            start_idx = max(0, ttl_idx + epoch_start)
            end_idx = min(len(electrode_data), ttl_idx + epoch_end)

            # エポックデータを取得し、リストに追加
            epoch_data = electrode_data[start_idx:end_idx]
            if len(epoch_data) == num_samples:
                epoch_summary_data[electrode].append(epoch_data.tolist())

        except Exception as e:
            print(f"{electrode} - TTL {ttl} の処理中にエラーが発生しました: {e}")

# 統合データの保存処理
for electrode, data in epoch_summary_data.items():
    if data:
        summary_df = pd.DataFrame(data).T
        time_column = pd.Series(np.arange(epoch_start, epoch_end), name="Time [ms]")
        summary_df.insert(0, "Time [ms]", time_column)
        summary_df.columns = ["Time [ms]"] + [f"Epoch {i+1}" for i in range(len(data))]
        summary_csv_path = os.path.join(summary_output_dir, f"{electrode}_epoch_summary.csv")
        summary_df.to_csv(summary_csv_path, index=False, encoding='utf-8-sig')
        print(f"{electrode} の統合データを {summary_csv_path} に保存しました。")
    else:
        print(f"{electrode} の統合データが空です。")

end_time = datetime.now()
elapsed_time = end_time - start_time
print(f"プログラム終了時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"実行時間: {elapsed_time}")
