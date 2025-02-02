#############################################################################################
#  2024/12/23 作成
#  2025/01/06 改訂
#  2025/01/08 改訂
#  2025/2/2 再改訂（TTL線削除）
#
#  --周波数共通, エラーなしセッション用--
# 【4_colave.py の後に実行すること】
#
# 【概要】Correct試行波形のプロット（Error試行なし）
# 加算平均データをもとに、Correct試行の波形プロットを作成し、
# 各電極ごとにPNG形式で "result" ディレクトリに保存する。
#
# 【処理内容】
# 1. "calc/comp" から各電極の加算平均データ（Correct試行）を読み取る
# 2. 各電極ごとにCorrect試行の波形プロットを作成
# 3. 元の範囲（-1000ms～2000ms）と拡大範囲（-500ms～1000ms）の2種類を作成
# 4. プロット画像を "result" ディレクトリに保存
#
# 【出力先】
# - "result/original"（元の範囲のプロット）
# - "result/zoomed"（拡大範囲のプロット）
#
#############################################################################################

import pandas as pd
import matplotlib.pyplot as plt
import os
from tkinter.filedialog import askdirectory

# GUIで解析のルートディレクトリを選択
root_dir = askdirectory(title="解析のルートディレクトリを選択してください")

# 比較用CSVファイルのディレクトリ設定
comp_dir = os.path.join(root_dir, "calc", "comp")

# プロットの出力先ディレクトリ設定
result_dir = os.path.join(root_dir, "result")
os.makedirs(result_dir, exist_ok=True)

# TTL線の表示設定
SHOW_TTL = False  # TrueにするとTTL線が表示されます

# 電極リスト
electrodes = ["Cz", "F3", "F4", "FCz", "Fz"]

# プロット作成関数
def plot_data(data, electrode, zoom=False):
    plt.figure(figsize=(10, 6))
    plt.plot(data["Time [ms]"], data["Correct Average [μV]"], label="Correct", color="blue")
    if SHOW_TTL:
        plt.axvline(0, color="brown", linestyle="--", label="TTL Signal")
    plt.axhline(0, color="black", linestyle="--", linewidth=0.8)
    plt.axvline(0, color="black", linestyle="--", linewidth=0.8)
    plt.title(f"{electrode}", fontsize=20)
    if zoom:
        plt.xlabel("Time [ms]", fontsize=20)
        plt.xlim(-400, 1000)
        plt.xticks(ticks=[-400, -200, 0, 200, 400, 600, 800, 1000], fontsize=16)
    else:
        plt.xlabel("Time [s]", fontsize=20)
        plt.xlim(-1000, 2000)
        plt.xticks(ticks=[-1000, -500, 0, 500, 1000, 1500, 2000], labels=["-1", "-0.5", "0", "0.5", "1", "1.5", "2"], fontsize=16)
    plt.ylabel("Amplitude [μV]", fontsize=20)
    plt.yticks(fontsize=16)
    plt.ylim(-7, 7)
    plt.legend(fontsize=18)
    file_suffix = "zoomed" if zoom else "original"
    file_path = os.path.join(result_dir, f"{electrode}_{file_suffix}.png")
    plt.savefig(file_path, dpi=300)
    plt.close()

# 各電極の比較用CSVファイルを読み込み、プロットを作成
for electrode in electrodes:
    file_path = os.path.join(comp_dir, electrode, f"{electrode}_comp.csv")

    if os.path.exists(file_path):
        data = pd.read_csv(file_path)
        plot_data(data, electrode, zoom=False)
        plot_data(data, electrode, zoom=True)
    else:
        print(f"{file_path} が見つかりませんでした。")

print("すべてのプロットを作成し、保存しました。")

