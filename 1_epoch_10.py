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

# ✅ GUIを使ったディレクトリ選択関数
def select_directory(prompt):
    print(prompt)
    Tk().withdraw()
    return askdirectory(title=prompt)

# ✅ GUIを使ったファイル選択関数
def select_file(prompt):
    print(prompt)
    Tk().withdraw()
    return askopenfilename(title=prompt)

# ✅ 解析のルートディレクトリをユーザーに選択させる
root_dir = select_directory("解析のルートディレクトリを選択してください")
calc_dir = os.path.join(root_dir, "calc")
epoch_output_dir = os.path.join(calc_dir, "epoch")
os.makedirs(epoch_output_dir, exist_ok=True)

# ✅ 生データ（CSV）とICA処理済みデータのファイルを選択
raw_data_file = select_file("生データ（.csv）のファイルを選択してください。")
ica_data_file = select_file("ICA処理済みデータ（.csv）のファイルを選択してください。")

# ✅ データの読み込み
try:
    raw_data = pd.read_csv(raw_data_file, encoding='windows-1252')
    ica_data = pd.read_csv(ica_data_file)
except Exception as e:
    print(f"データ読み込み中にエラーが発生しました: {e}")
    raise

# ✅ 電極リスト
electrodes = ["F3", "Fz", "F4", "FCz", "Cz"]

# ✅ 時間データの取得
try:
    time_data = np.round(ica_data.iloc[:, 0].values * 1000, decimals=6)  # Time列の取得と丸め
except Exception as e:
    print(f"時間データの取得中にエラーが発生しました: {e}")
    raise

# ✅ TTL信号の取得
ttl_times = np.round(raw_data.iloc[5:61, 9].values * 1000, decimals=6)  # TTL信号を[s]から[ms]に変換して丸め

# ✅ 各TTL信号のタイミングを最も近い値で一致判定
valid_ttl_times = []
for ttl in ttl_times:
    closest_idx = np.searchsorted(time_data, ttl)
    if closest_idx < len(time_data) and abs(time_data[closest_idx] - ttl) < 1:
        valid_ttl_times.append(time_data[closest_idx])
print(f"有効なTTL信号の数: {len(valid_ttl_times)}")

# ✅ エポック範囲とサンプリング設定
epoch_start = -1000
epoch_end = 2000
num_samples = epoch_end - epoch_start

# ✅ 各電極の統合データを保持する辞書
epoch_summary_data = {electrode: [] for electrode in electrodes}

# ✅ 各電極ごとにエポック処理
for electrode in electrodes:
    original_plot_dir = os.path.join(epoch_output_dir, "original", electrode)
    zoomed_plot_dir = os.path.join(epoch_output_dir, "zoomed", electrode)
    os.makedirs(original_plot_dir, exist_ok=True)
    os.makedirs(zoomed_plot_dir, exist_ok=True)

    electrode_data = ica_data[electrode].values
    epoch_time = np.arange(epoch_start, epoch_end)  # ✅ Time列の生成

    for i, ttl in enumerate(valid_ttl_times):
        try:
            ttl_idx = np.abs(time_data - ttl).argmin()
            start_idx = max(0, ttl_idx + epoch_start)
            end_idx = min(len(electrode_data), ttl_idx + epoch_end)

            # ✅ エポックデータを取得し、リストに追加
            epoch_data = electrode_data[start_idx:end_idx]
            if len(epoch_data) == num_samples:
                epoch_summary_data[electrode].append(epoch_data.tolist())

            # ✅ オリジナルサイズのプロット
            plt.figure(figsize=(10, 5), num=f"{electrode}_original_{i+1}")
            plt.plot(epoch_time[:num_samples], epoch_data[:num_samples], label=f'TTL {i+1}')
            plt.axvline(0, color='brown', linestyle='--', label='TTL Signal')
            plt.axhline(0, color='black', linestyle='-', linewidth=0.8)
            plt.xticks(np.arange(epoch_start, epoch_end + 1, 500), fontsize=16)
            plt.yticks(np.arange(-15, 16, 5), fontsize=16)
            plt.title(f'{electrode} Epoch {i+1}', fontsize=20)
            plt.xlabel('Time [ms]', fontsize=20)
            plt.ylabel('Amplitude [μV]', fontsize=20)
            plt.legend(fontsize=18)
            plt.xlim(epoch_start, epoch_end)
            plt.ylim(-16, 16)
            plt.grid(which='both')
            plot_path = os.path.join(original_plot_dir, f'epoch_{i+1}.png')
            plt.savefig(plot_path, dpi=300)
            plt.close(f"{electrode}_original_{i+1}")

            # ✅ 拡大サイズのプロット
            plt.figure(figsize=(10, 5), num=f"{electrode}_zoomed_{i+1}")
            plt.plot(epoch_time[:num_samples], epoch_data[:num_samples], label=f'TTL {i+1}')
            plt.axvline(0, color='brown', linestyle='--', label='TTL Signal')
            plt.axhline(0, color='black', linestyle='-', linewidth=0.8)
            plt.xticks(np.arange(-500, 501, 100), fontsize=16)
            plt.minorticks_on()
            plt.gca().xaxis.set_minor_locator(MultipleLocator(100))
            plt.yticks(np.arange(-15, 16, 5), fontsize=16)
            plt.title(f'{electrode} Epoch {i+1}', fontsize=20)
            plt.xlabel('Time [ms]', fontsize=20)
            plt.ylabel('Amplitude [μV]', fontsize=20)
            plt.legend(fontsize=18)
            plt.xlim(-500, 500)
            plt.ylim(-16, 16)
            plt.grid(which='both', linestyle='--', linewidth=0.5)
            zoomed_plot_path = os.path.join(zoomed_plot_dir, f'epoch_{i+1}.png')
            plt.savefig(zoomed_plot_path, dpi=300)
            plt.close(f"{electrode}_zoomed_{i+1}")

        except Exception as e:
            print(f"{electrode} - エポック {i+1} の処理中にエラーが発生しました: {e}")

# ✅ 統合データの保存先ディレクトリを設定
summary_output_dir = os.path.join(calc_dir, "epoch_summary")
os.makedirs(summary_output_dir, exist_ok=True)

# ✅ 統合データの保存処理
for electrode, data in epoch_summary_data.items():
    if data:
        # データを転置し、各エポックのデータを列として保存
        summary_df = pd.DataFrame(data).T

        # -1000msから2000msの時間データを作成
        time_column = pd.Series(np.arange(epoch_start, epoch_end), name="Time [ms]")

        # Time列を最左列に追加
        summary_df.insert(0, "Time [ms]", time_column)

        # ✅ エポック番号を1から始めるようにカラム名を修正
        summary_df.columns = ["Time [ms]"] + [f"Epoch {i+1}" for i in range(len(data))]

        # ✅ CSVファイルとして保存
        summary_csv_path = os.path.join(summary_output_dir, f"{electrode}_epoch_summary.csv")
        summary_df.to_csv(summary_csv_path, index=False, encoding='utf-8-sig')
        print(f"{electrode} の統合データを {summary_csv_path} に保存しました。")
    else:
        print(f"{electrode} の統合データが空です。")

end_time = datetime.now()
elapsed_time = end_time - start_time
print(f"プログラム終了時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"実行時間: {elapsed_time}")
