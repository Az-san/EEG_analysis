#############################################################################################
#  2024/12/23 作成
#  2025/01/06 改訂
#  025/2/2 再改訂（TTL線削除）, ラベル修正
#
#  --周波数共通, エラーありセッション--
# 【4_colave.py の後に実行すること】
#
# 【概要】Correct試行, Error試行, 差分波形のプロット
# 加算平均データおよび比較用データから、Correct試行とError試行の差分波形プロットを作成し、
# 各電極ごとにPNG形式で "result" ディレクトリに保存する。
#
# 【処理内容】
# 1. "calc/ave" から各電極の加算平均データを読み取る
# 2. "calc/comp" から比較用データを読み取る
# 3. 各電極ごとにCorrect、Error、差分波形のプロットを作成
# 4. 元の範囲（-1000ms～2000ms）と拡大範囲（-500ms～1000ms）の2種類を作成
# 5. プロット画像を "result" ディレクトリに保存
#
# 【出力先】
# - "result"
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
    plt.figure(figsize=(16, 9))
    
    # 線を太くするために linewidth=3 を追加
    plt.plot(data["Time [ms]"], data["Correct Average [μV]"], label="Correct", color="blue", linewidth=3)
    plt.plot(data["Time [ms]"], data["Error Average [μV]"], label="Error", color="red", linewidth=3)
    plt.plot(data["Time [ms]"], data["Difference [μV]"], label="Difference", color="green", linewidth=3)
    
    if SHOW_TTL:
        plt.axvline(0, color="brown", linestyle="--", label="TTL Signal", linewidth=2)
    
    # 基準線も少し太くする
    plt.axhline(0, color="black", linestyle="--", linewidth=1.5)
    plt.axvline(0, color="black", linestyle="--", linewidth=1.5)

    title = f"{electrode}" if not zoom else f"{electrode}"
    plt.title(title, fontsize=50)

    if zoom:
        plt.xlabel("Time [ms]", fontsize=40, labelpad=20)
        plt.xlim(-400, 1000)
        plt.xticks(ticks=[-400, -200, 0, 200, 400, 600, 800, 1000], fontsize=30)
    else:
        plt.xlabel("Time [s]", fontsize=40, labelpad=20)
        plt.xlim(-1000, 2000)
        plt.xticks(ticks=[-1000, -500, 0, 500, 1000, 1500, 2000], 
                   labels=["-1", "-0.5", "0", "0.5", "1", "1.5", "2"], fontsize=30)
    
    plt.ylabel("Amplitude [μV]", fontsize=40, labelpad=20)
    plt.yticks(fontsize=30)
    plt.ylim(-7, 7)

    plt.legend(fontsize=30, loc='upper right')
    plt.tight_layout()

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
