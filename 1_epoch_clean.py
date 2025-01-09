#######################################################################################################
#  2024/12/23 作成
#  2025/01/06 改訂
#
# 【概要】エポック切り出し
# 生データとICA処理済みデータを基に、TTL信号のタイミングを基準にエポックデータを切り出し、各電極のエポックデータを統合して "calc/epoch_summary" に保存する。
# また、各エポックの波形プロットを作成し、電極ごとに "calc/epoch_plots/{電極名}" に保存する。
#
# 【処理内容】
# 1. 生データ（raw_data.csv）およびICA処理済みデータ（ica_data.csv）をGUIで選択する
# 2. 生データからTTL信号のタイミング情報を取得する
#    - TTL信号のタイミングは、生データの9列目（0インデックスで8番目）に格納されている
#    - TTL信号のタイミングがデータ範囲外にならないよう、最大時間範囲内のデータのみを使用する
# 3. 各TTL信号のタイミングを基に、各電極ごとのエポックデータを切り出す
#    - 各エポックはTTL信号を基準に、-1000ms（-1秒）から+2000ms（+2秒）の範囲で切り出す
#    - エポックデータのサンプリング周波数は1000Hz（1ms間隔）
# 4. エポックデータを電極ごとにCSVファイルとして保存する
#    - ファイル名形式: "epoch_{エポック番号}_{電極名}.csv"
#    - 保存先: "calc/epoch_plots/{電極名}/"
# 5. 各エポックの波形をプロットし、PNGファイルとして保存する。
#    - プロットにはTTL信号の絶対時刻（赤線）およびエポックの開始/終了時刻（青線/緑線）を表示する
#    - 縦軸は振幅（Amplitude）[μV]、横軸は時間（Time）[s]
#    - 各電極ごとのプロット画像は "calc/epoch_plots/{電極名}/" に保存する
# 6. 各電極の全エポックデータを統合し、"calc/epoch_summary" にCSVファイルとして保存する
#    - ファイル名形式: "{電極名}_epoch_summary.csv"
#    - データは各エポックごとに1列として保存される（例: Epoch 1, Epoch 2, ...）。
#
# 【出力先ディレクトリ】
# - エポックデータの統合CSV: "calc/epoch_summary"
# - エポックごとの波形プロット: "calc/epoch_plots/{電極名}"
#
# 【注意点】
# - 生データのファイル形式はCSV、エンコーディングは "windows-1252"。
# - ICA処理済みデータのファイル形式はCSV（スペース区切り）、エンコーディングは "shift-jis"。
# - TTL信号のタイミングが-1000msから+2000msの範囲内に収まることを確認する！！
#######################################################################################################


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory
from matplotlib.ticker import MultipleLocator
from datetime import datetime #プログラムの時間計測してるだけ、べつにいらない


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
os.makedirs(calc_dir, exist_ok=True)

# ✅ 生データ（CSV）とICA処理済みデータのファイルを選択
raw_data_file = select_file("生データ（.csv）のファイルを選択してください。")
ica_data_file = select_file("ICA処理済みデータ（.csv）のファイルを選択してください。")

# ✅ データの読み込み
try:
    raw_data = pd.read_csv(raw_data_file, encoding='windows-1252')
    ica_data = pd.read_csv(ica_data_file, header=None)
    print("✅ 生データとICA処理済みデータが正常に読み込まれました。")
    print(f"📊 ICA処理済みデータの行数: {len(ica_data)}, 列数: {ica_data.shape[1]}")
except Exception as e:
    print(f"データ読み込み中にエラーが発生しました: {e}")
    raise

# ✅ 電極と対応する列番号
electrodes = {
    "F3": 0,
    "Fz": 1,
    "F4": 2,
    "FCz": 3,
    "Cz": 4
}

# ✅ 時間データの生成（1行目 = 1[ms], 2行目 = 2[ms], ...）
if len(ica_data) > 0:
    time_data_ms = np.arange(1, len(ica_data) + 1)
else:
    raise ValueError("ICA処理済みデータが空です。")

# ✅ TTL信号の取得（生データから）
ttl_times_ms = raw_data.iloc[5:61, 9].astype(float).values * 1000  # [s] → [ms]に変換

# ✅ TTL信号がデータ範囲内か確認して有効なTTLタイミングを取得
valid_ttl_times = [ttl for ttl in ttl_times_ms if ttl + 2000 <= time_data_ms[-1]]

# ✅ エポック範囲とサンプリング設定
epoch_start = -1000
epoch_end = 2000
num_samples = epoch_end - epoch_start

# ✅ 各電極の統合データを保持する辞書
epoch_summary_data = {electrode: [] for electrode in electrodes.keys()}

# ✅ エポックデータの保存先ディレクトリ設定
epoch_output_dir = os.path.join(calc_dir, "epoch")
os.makedirs(epoch_output_dir, exist_ok=True)

# ✅ 各電極ごとにエポック処理
for electrode, col_idx in electrodes.items():
    original_plot_dir = os.path.join(epoch_output_dir, "original", electrode)
    zoomed_plot_dir = os.path.join(epoch_output_dir, "zoomed", electrode)
    os.makedirs(original_plot_dir, exist_ok=True)
    os.makedirs(zoomed_plot_dir, exist_ok=True)

    electrode_data = ica_data.iloc[:, col_idx].values

    for i, ttl in enumerate(valid_ttl_times):
        try:
            ttl_idx = np.where(np.round(time_data_ms) == np.round(ttl))[0][0]
            start_idx = ttl_idx + epoch_start
            end_idx = ttl_idx + epoch_end

            epoch_data = electrode_data[start_idx:end_idx]
            epoch_time = time_data_ms[start_idx:end_idx] / 1000

            epoch_summary_data[electrode].append(epoch_data.tolist())

            # オリジナルサイズのプロット
            plt.figure(figsize=(10, 5))
            plt.plot(epoch_time, epoch_data, label=f'TTL {i+1}')
            plt.axvline(ttl / 1000, color='brown', linestyle='--', label='TTL Signal')
            plt.axhline(0, color='black', linestyle='-', linewidth=0.8)
            plt.xticks(np.arange((ttl - 1000) / 1000, (ttl + 2000) / 1000 + 0.5, 0.5), fontsize=16)
            plt.yticks(np.arange(-15, 16, 5), fontsize=16)
            plt.title(f'{electrode} Epoch {i+1}', fontsize=20)
            plt.xlabel('Time [s]', fontsize=20)
            plt.ylabel('Amplitude [μV]', fontsize=20)
            plt.legend(fontsize=18)
            plt.xlim(ttl / 1000 - 1.0, ttl / 1000 + 2.0)
            plt.ylim(-16, 16)
            plt.grid(which='both')
            plot_path = os.path.join(original_plot_dir, f'epoch_{i+1}.png')
            plt.savefig(plot_path, dpi=300)
            plt.close()

            # 拡大サイズのプロット
            plt.figure(figsize=(10, 5))
            plt.plot(epoch_time, epoch_data, label=f'TTL {i+1}')
            plt.axvline(ttl / 1000, color='brown', linestyle='--', label='TTL Signal')
            plt.axhline(0, color='black', linestyle='-', linewidth=0.8)
            plt.xticks(np.arange(ttl / 1000 - 0.5, ttl / 1000 + 0.6, 0.5), fontsize=16)
            plt.minorticks_on()
            plt.gca().xaxis.set_minor_locator(MultipleLocator(0.1))
            plt.yticks(np.arange(-15, 16, 5), fontsize=16)
            plt.title(f'{electrode} Epoch {i+1}', fontsize=20)
            plt.xlabel('Time [s]', fontsize=20)
            plt.ylabel('Amplitude [μV]', fontsize=20)
            plt.legend(fontsize=18)
            plt.xlim(ttl / 1000 - 0.5, ttl / 1000 + 1.0)
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
        summary_df = pd.DataFrame(np.array(data).T)  # 転置して右方向にエポックを展開
        time_column = pd.Series(np.arange(epoch_start, epoch_end), name="TIME")
        summary_df.insert(0, "TIME", time_column)
        summary_csv_path = os.path.join(summary_output_dir, f"{electrode}_epoch_summary.csv")
        summary_df.to_csv(summary_csv_path, index=False, encoding='utf-8-sig')
        print(f"{electrode} の統合データを {summary_csv_path} に保存しました。")

end_time = datetime.now()
elapsed_time = end_time - start_time
print(f"プログラム終了時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"実行時間: {elapsed_time}")

