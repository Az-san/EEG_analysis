#############################################################################################
#  2024/12/23 作成
#  2025/01/06 改訂
#  2025/01/08 改訂
#
# 【4_ave_plot.py の後に実行すること！】
#
# 【概要】Correct試行, Error試行, 差分波形のプロット
# 加算平均データおよび比較用データをもとに、Error 試行と Correct 試行の波形プロットを作成し、各電極ごとの PNG ファイルとして保存する。
# 加算平均波形は "calc/ave" ディレクトリから、比較用波形は "calc/comp" ディレクトリから読み取る。
# 各電極ごとに個別プロットおよび比較プロットを作成し、すべてのプロット画像を "result" ディレクトリに保存する。
#
# 【処理内容】
# 1. "calc/ave" ディレクトリから各電極の加算平均 CSV ファイルを読み取る
#    - 各電極の Correct 試行と Error 試行の加算平均波形を取得
# 2. "calc/comp" ディレクトリから各電極の比較用 CSV ファイルを読み取る
#    - 比較用 CSV には、Error 試行の加算平均、Correct 試行の加算平均、およびその差分（Difference）が含まれる
# 3. 各電極ごとに以下のプロットを作成する
#    - 個別プロット: Correct 試行の波形（青色）と Error 試行の波形（赤色）を描画
#    - 比較プロット: Correct 試行、Error 試行、および差分波形（緑色）を同一プロット上に描画
# 4. すべてのプロット画像を "result" ディレクトリに PNG ファイルとして保存する
#    - 個別プロット: "{電極名}_correct.png" および "{電極名}_error.png"
#    - 比較プロット: "{電極名}_comp.png"
#
# 【プロットの仕様】
# - 横軸: 時間 [ms]（範囲: -1000ms ～ 2000ms）
# - 縦軸: 振幅 [μV]（範囲: -7 ～ 7 μV）
# - TTL 信号の位置は茶色の破線で示す
# - 縦軸ゼロの位置には黒色の水平線を追加
# - 横軸は 500ms ごとにラベルを表示し、100ms ごとに目盛り線を引く
# - 縦軸は 2 μV ごとにラベルを表示し、1 μV ごとに目盛り線を引く
#
# 【出力先ディレクトリ】
# - "result"（すべての PNG ファイルをこのディレクトリに保存）
#
# 【出力ファイルの例】
# - Cz_correct.png
# - Cz_error.png
# - Cz_comp.png
# - F3_correct.png
# - F3_error.png
# - F3_comp.png　など
#############################################################################################



import pandas as pd
import matplotlib.pyplot as plt
import os
from tkinter.filedialog import askdirectory

# ✅ GUIで解析のルートディレクトリを選択
root_dir = askdirectory(title="解析のルートディレクトリを選択してください")

# ✅ 比較用CSVファイルのディレクトリ設定
comp_dir = os.path.join(root_dir, "calc", "comp")

# ✅ プロットの出力先ディレクトリ設定
original_plot_dir = os.path.join(root_dir, "result", "original")
zoomed_plot_dir = os.path.join(root_dir, "result", "zoomed")
os.makedirs(original_plot_dir, exist_ok=True)
os.makedirs(zoomed_plot_dir, exist_ok=True)

# 電極リスト
electrodes = ["Cz", "F3", "F4", "FCz", "Fz"]

# 各電極の比較用CSVファイルを読み込み、プロットを作成
for electrode in electrodes:
    file_path = os.path.join(comp_dir, electrode, f"{electrode}_comp.csv")

    if os.path.exists(file_path):
        # CSVファイルの読み込み
        data = pd.read_csv(file_path)

        # ✅ Correct試行のプロット（元の範囲）
        plt.figure(figsize=(10, 6))
        plt.plot(data["Time [ms]"], data["Correct Average [μV]"], label="Correct", color="blue")
        plt.axvline(0, color="brown", linestyle="--", label="TTL Signal")
        plt.axhline(0, color="black", linestyle="-", linewidth=0.8)
        plt.title(f"{electrode} Correct Trial", fontsize=20)
        plt.xlabel("Time [ms]", fontsize=20)
        plt.ylabel("Amplitude [μV]", fontsize=20)
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        plt.xlim(-1000, 2000)
        plt.ylim(-7, 7)
        plt.grid(True)
        plt.legend(fontsize=18)
        correct_plot_path = os.path.join(original_plot_dir, f"{electrode}_correct.png")
        plt.savefig(correct_plot_path, dpi=300)
        plt.close()
        print(f"{correct_plot_path} に保存しました。")

        # ✅ Correct試行のプロット（拡大範囲）
        plt.figure(figsize=(10, 6))
        plt.plot(data["Time [ms]"], data["Correct Average [μV]"], label="Correct", color="blue")
        plt.axvline(0, color="brown", linestyle="--", label="TTL Signal")
        plt.axhline(0, color="black", linestyle="-", linewidth=0.8)
        plt.title(f"{electrode} Correct Trial", fontsize=20)
        plt.xlabel("Time [ms]", fontsize=20)
        plt.ylabel("Amplitude [μV]", fontsize=20)
        plt.xticks(ticks=range(-500, 1001, 500), fontsize=16)
        plt.minorticks_on()
        plt.gca().xaxis.set_minor_locator(plt.MultipleLocator(100))  # 縦線を100msごとに
        plt.yticks(fontsize=16)
        plt.xlim(-500, 1000)
        plt.ylim(-7, 7)
        plt.grid(True)
        plt.legend(fontsize=18)
        correct_zoomed_plot_path = os.path.join(zoomed_plot_dir, f"{electrode}_correct_zoomed.png")
        plt.savefig(correct_zoomed_plot_path, dpi=300)
        plt.close()
        print(f"{correct_zoomed_plot_path} に保存しました。")
        
    else:
        print(f"{file_path} が見つかりませんでした。")

print("すべてのプロットを作成し、保存しました。")
