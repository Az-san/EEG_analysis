#######################################################################################################
#  2024/12/23 作成
#  2025/01/06 改訂
#  2025/01/08 再改訂
#  2025/02/02 再々改訂（波形プロット部削除）
#
#  --1000Hz, エラーありセッション用--
#  【最初に実行する】
#  
# 【概要】エポック切り出しと波形プロット
# 生データとICA処理済みデータからTTL信号を基準にエポックを切り出し、各電極のエポックデータをCSV保存する
#
# 【処理内容】
# 1. 生データ（raw_data.csv）とICA処理済みデータ（ica_data.csv）をGUIで選択
# 2. TTL信号（生データ9列目）に基づき、-1〜+2秒のエポックデータを切り出す
#
# 【出力先】
# - 統合CSV: "calc/epoch_summary"
#
# 【注意】
# - 生データ: CSV形式、"windows-1252"エンコーディング
# - ICAデータ: CSV（スペース区切り）、"shift-jis"エンコーディング
# - TTL信号が-1000ms〜+2000msの範囲内であることを確認
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
ica_data_file = select_file("ICA処理済みデータ（.csv）のファイルを選択してください。")

# データの読み込み
try:
    raw_data = pd.read_csv(raw_data_file, encoding='windows-1252')
    ica_data = pd.read_csv(ica_data_file, header=None)
    print("✅ 生データとICA処理済みデータが正常に読み込まれました。")
except Exception as e:
    print(f"データ読み込み中にエラーが発生しました: {e}")
    raise

# 電極と対応する列番号
electrodes = {
    "F3": 0,
    "Fz": 1,
    "F4": 2,
    "FCz": 3,
    "Cz": 4
}

# 時間データの生成（1行目 = 1[ms], 2行目 = 2[ms], ...）
time_data_ms = np.arange(1, len(ica_data) + 1)

# TTL信号の取得
ttl_times_ms = raw_data.iloc[5:61, 9].astype(float).values * 1000  # [s] → [ms]に変換

# TTL信号がデータ範囲内か確認して有効なTTLタイミングを取得
valid_ttl_times = [ttl for ttl in ttl_times_ms if ttl + 2000 <= time_data_ms[-1]]

# エポック範囲とサンプリング設定
epoch_start = -1000
epoch_end = 2000
num_samples = epoch_end - epoch_start

# 各電極の統合データを保持する辞書
epoch_summary_data = {electrode: [] for electrode in electrodes.keys()}

# 各電極ごとにエポック処理
for electrode, col_idx in electrodes.items():
    electrode_data = ica_data.iloc[:, col_idx].values

    for ttl in valid_ttl_times:
        try:
            ttl_idx = np.where(np.round(time_data_ms) == np.round(ttl))[0][0]
            start_idx = ttl_idx + epoch_start
            end_idx = ttl_idx + epoch_end

            epoch_data = electrode_data[start_idx:end_idx]
            epoch_summary_data[electrode].append(epoch_data.tolist())

        except Exception as e:
            print(f"{electrode} - TTL {ttl} の処理中にエラーが発生しました: {e}")

# 統合データの保存処理
for electrode, data in epoch_summary_data.items():
    if data:
        summary_df = pd.DataFrame(np.array(data).T)
        time_column = pd.Series(np.arange(epoch_start, epoch_end), name="TIME")
        summary_df.insert(0, "TIME", time_column)
        summary_csv_path = os.path.join(summary_output_dir, f"{electrode}_epoch_summary.csv")
        summary_df.to_csv(summary_csv_path, index=False, encoding='utf-8-sig')
        print(f"{electrode} の統合データを {summary_csv_path} に保存しました。")
    else:
        print(f"{electrode} の統合データが空です。")

end_time = datetime.now()
elapsed_time = end_time - start_time
print(f"プログラム終了時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"実行時間: {elapsed_time}")
