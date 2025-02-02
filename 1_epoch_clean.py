#######################################################################################################
#  2024/12/23 作成
#  2025/01/06 改訂
#
#  --1000Hz, エラーなしセッション--
#  【最初に実行する】
#
# 【概要】エポック切り出し
# 生データとICA処理済みデータから、TTL信号を基準に-1〜+2秒のエポックデータを切り出し、
# 各電極ごとにCSV保存と波形プロットを行う。
#
# 【処理内容】
# 1. 生データ（raw_data.csv）およびICA処理済みデータ（ica_data.csv）をGUIで選択
# 2. TTL信号（生データ9列目）に基づき、各電極のエポックデータを切り出す
# 3. 切り出したエポックデータを "calc/epoch_summary" にCSV形式で保存
# 4. 各エポックの波形をプロットし、 "calc/epoch_plots/{電極名}" にPNG形式で保存
#
# 【出力先】
# - 統合CSV: "calc/epoch_summary"
# - 波形プロット: "calc/epoch_plots/{電極名}"
#
# 【注意】
# - 生データ: CSV形式、"windows-1252"エンコーディング
# - ICAデータ: CSV（スペース区切り）、"shift-jis"エンコーディング
# - TTL信号が-1〜+2秒内に収まることを確認すること！
#######################################################################################################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory
from matplotlib.ticker import MultipleLocator
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
epoch_output_dir = os.path.join(calc_dir, "epoch")
os.makedirs(epoch_output_dir, exist_ok=True)

# 生データ（CSV）とICA処理済みデータのファイルを選択
raw_data_file = select_file("生データ（.csv）のファイルを選択してください。")
ica_data_file = select_file("ICA処理済みデータ（.csv）のファイルを選択してください。")

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
    time_data = ica_data.iloc[:, 0].values  # Time列の取得
except Exception as e:
    print(f"時間データの取得中にエラーが発生しました: {e}")
    raise

# サンプリング周波数の計算
sampling_intervals = np.diff(time_data)  # 時間間隔の計算
average_interval = np.mean(sampling_intervals)  # 平均間隔
print(f"平均サンプリング間隔: {average_interval} 秒")

# TTL信号の取得
ttl_times = raw_data.iloc[5:61, 9].values  # TTL信号の取得（秒単位のまま）

# TTL信号を2-10Hz用に補正
adjusted_ttl_times = ttl_times * (average_interval / 0.001)  # 0.001は1ms間隔に対応
print(f"補正後のTTL信号: {adjusted_ttl_times}")

# 各TTL信号のタイミングをTime列に基づいて一致判定
valid_ttl_times = []
for ttl in adjusted_ttl_times:
    ttl_indices = np.where(np.round(time_data, decimals=6) == np.round(ttl, decimals=6))[0]
    if len(ttl_indices) > 0:
        valid_ttl_times.append(time_data[ttl_indices[0]])
    else:
        print(f"TTL {ttl} に一致する時間が見つかりませんでした。")

# エポック範囲とサンプリング設定
epoch_start = -1.0  # [s]
epoch_end = 2.0  # [s]

# 各電極の統合データを保持する辞書
epoch_summary_data = {electrode: [] for electrode in electrodes}

# 各電極ごとにエポック処理
for electrode in electrodes:
    original_plot_dir = os.path.join(epoch_output_dir, "original", electrode)
    zoomed_plot_dir = os.path.join(epoch_output_dir, "zoomed", electrode)
    os.makedirs(original_plot_dir, exist_ok=True)
    os.makedirs(zoomed_plot_dir, exist_ok=True)

    electrode_data = ica_data[electrode].values

    for i, ttl in enumerate(valid_ttl_times):
        try:
            ttl_idx = np.where(np.round(time_data, decimals=6) == np.round(ttl, decimals=6))[0][0]
            start_idx = np.abs(time_data - (ttl + epoch_start)).argmin()
            end_idx = np.abs(time_data - (ttl + epoch_end)).argmin()

            epoch_data = electrode_data[start_idx:end_idx]
            epoch_time = time_data[start_idx:end_idx]

            epoch_summary_data[electrode].append(epoch_data.tolist())

            # オリジナルサイズのプロット
            plt.figure(figsize=(10, 5))
            plt.plot(epoch_time, epoch_data, label=f'TTL {i+1}')
            plt.axvline(ttl, color='brown', linestyle='--', label='TTL Signal')
            plt.axhline(0, color='black', linestyle='-', linewidth=0.8)
            plt.xticks(np.arange(ttl - 1.0, ttl + 2.1, 0.5), fontsize=16)
            plt.yticks(np.arange(-15, 16, 5), fontsize=16)
            plt.title(f'{electrode} Epoch {i+1}', fontsize=20)
            plt.xlabel('Time [s]', fontsize=20)
            plt.ylabel('Amplitude [μV]', fontsize=20)
            plt.legend(fontsize=18)
            plt.xlim(ttl - 1.0, ttl + 2.0)
            plt.ylim(-16, 16)
            plt.grid(which='both')
            plot_path = os.path.join(original_plot_dir, f'epoch_{i+1}.png')
            plt.savefig(plot_path, dpi=300)
            plt.close()

            # 拡大サイズのプロット
            plt.figure(figsize=(10, 5))
            plt.plot(epoch_time, epoch_data, label=f'TTL {i+1}')
            plt.axvline(ttl, color='brown', linestyle='--', label='TTL Signal')
            plt.axhline(0, color='black', linestyle='-', linewidth=0.8)
            plt.xticks(np.arange(ttl - 0.5, ttl + 0.6, 0.1), fontsize=16)
            plt.minorticks_on()
            plt.gca().xaxis.set_minor_locator(MultipleLocator(0.1))
            plt.yticks(np.arange(-15, 16, 5), fontsize=16)
            plt.title(f'{electrode} Epoch {i+1}', fontsize=20)
            plt.xlabel('Time [s]', fontsize=20)
            plt.ylabel('Amplitude [μV]', fontsize=20)
            plt.legend(fontsize=18)
            plt.xlim(ttl - 0.5, ttl + 0.5)
            plt.ylim(-16, 16)
            plt.grid(which='both', linestyle='--', linewidth=0.5)
            zoomed_plot_path = os.path.join(zoomed_plot_dir, f'epoch_{i+1}.png')
            plt.savefig(zoomed_plot_path, dpi=300)
            plt.close()

        except Exception as e:
            print(f"{electrode} - エポック {i+1} の処理中にエラーが発生しました: {e}")

# 統合データの保存先ディレクトリを設定
summary_output_dir = os.path.join(calc_dir, "epoch_summary")
os.makedirs(summary_output_dir, exist_ok=True)

# 統合データの保存処理
for electrode, data in epoch_summary_data.items():
    if data:
        summary_df = pd.DataFrame(data).T  # データフレームの転置
        time_column = pd.Series(epoch_time[:len(summary_df)], name="Time [s]")  # Time列を制限
        summary_df.insert(0, "Time [s]", time_column)
        summary_csv_path = os.path.join(summary_output_dir, f"{electrode}_epoch_summary.csv")
        summary_df.to_csv(summary_csv_path, index=False, encoding='utf-8-sig')
        print(f"{electrode} の統合データを {summary_csv_path} に保存しました。")

end_time = datetime.now()
elapsed_time = end_time - start_time
print(f"プログラム終了時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"実行時間: {elapsed_time}")
