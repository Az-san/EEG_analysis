#######################################################################################################
#  2024/12/23 作成
#  2025/01/06 改訂
#  2025/01/08 再改訂
#  2025/02/02 再々改訂
#
#  --1000Hz, エラーありセッション--
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
import matplotlib.pyplot as plt
import os
from tkinter import Tk
from tkinter.filedialog import askdirectory

# TTL線の表示設定
SHOW_TTL = False  # TrueにするとTTL線が表示されます

# GUIを使ったディレクトリ選択関数
def select_directory(prompt):
    print(prompt)
    Tk().withdraw()
    return askdirectory(title=prompt)

# 解析のルートディレクトリをユーザーに選択させる
root_dir = select_directory("解析のルートディレクトリを選択してください")
calc_dir = os.path.join(root_dir, "calc")
summary_output_dir = os.path.join(calc_dir, "epoch_summary")

# 電極リスト
electrodes = ["F3", "Fz", "F4", "FCz", "Cz"]

# 各電極の統合データを読み込み、波形プロットを作成
for electrode in electrodes:
    summary_csv_path = os.path.join(summary_output_dir, f"{electrode}_epoch_summary.csv")

    if os.path.exists(summary_csv_path):
        data = pd.read_csv(summary_csv_path)
        time = data["TIME"]

        # 各エポックのプロット
        for i in range(1, data.shape[1]):
            plt.figure(figsize=(8, 4))
            plt.plot(time, data.iloc[:, i])
            if SHOW_TTL:
                plt.axvline(0, color='brown', linestyle='--')
            plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
            plt.axvline(0, color='black', linestyle='--', linewidth=0.8)
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)
            plt.title(f'{electrode} Epoch {i}', fontsize=14)
            plt.xlabel('Time [ms]', fontsize=14)
            plt.ylabel('Amplitude [μV]', fontsize=14)
            plt.xlim(-1000, 2000)
            plt.ylim(-16, 16)

            plot_dir = os.path.join(calc_dir, "plots", electrode)
            os.makedirs(plot_dir, exist_ok=True)
            plt.savefig(os.path.join(plot_dir, f'epoch_{i}.png'), dpi=300)
            plt.close()

        print(f"{electrode} のプロットを保存しました。")
    else:
        print(f"{summary_csv_path} が見つかりませんでした。")