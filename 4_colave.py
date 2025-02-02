#############################################################################################
#  2024/12/23 作成
#  2025/01/06 改訂
#
# --Errorありなし共通, サンプリング周波数共通--
# 【3_sort_err.pyの後に実行すること】
#
# 【概要】加算平均の計算
# Correct試行とError試行の脳波データから加算平均波形を計算し、差分波形を生成するスクリプト。
# 加算平均の結果は "calc/ave" に保存し、Error試行とCorrect試行の差分波形は "calc/comp" に保存する。
#
# 【処理内容】
# 1. "correct" および "error" ディレクトリ内のデータ（CSV形式）を読み込む
# 2. 各電極ごとにCorrect試行とError試行の加算平均を計算し、"calc/ave" に保存
# 3. Error試行とCorrect試行の加算平均の差分波形を "calc/comp/{電極名}/" に保存
#
# 【出力先】
# - 加算平均: "calc/ave" （例: "{電極名}_correct_ave.csv", "{電極名}_error_ave.csv"）
# - 比較用CSV: "calc/comp/{電極名}/" （例: "{電極名}_comp.csv"）
#
#############################################################################################

import pandas as pd
import os
from tkinter import Tk
from tkinter.filedialog import askdirectory

# GUIで解析のルートディレクトリを選択
Tk().withdraw()
root_dir = askdirectory(title="解析のルートディレクトリを選択してください")

# CorrectデータとErrorデータのディレクトリ設定
correct_dir = os.path.join(root_dir, "calc", "correct")
error_dir = os.path.join(root_dir, "calc", "error")

# 出力先ディレクトリ
ave_output_dir = os.path.join(root_dir, "calc", "ave")
comp_output_dir = os.path.join(root_dir, "calc", "comp")
os.makedirs(ave_output_dir, exist_ok=True)
os.makedirs(comp_output_dir, exist_ok=True)

# 各電極の子ディレクトリ作成（比較用CSV用）
electrodes = ["Cz", "F3", "F4", "FCz", "Fz"]
for electrode in electrodes:
    os.makedirs(os.path.join(comp_output_dir, electrode), exist_ok=True)

# 加算平均の計算と保存
def calculate_grand_average(input_dir, output_dir, label):
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".csv"):
            file_path = os.path.join(input_dir, file_name)
            data = pd.read_csv(file_path, index_col=0)

            grand_average = data.mean(axis=1)

            electrode_name = file_name.split("_")[0]
            output_file = os.path.join(output_dir, f"{electrode_name}_{label}_ave.csv")
            grand_average.to_csv(output_file, header=["Amplitude [μV]"], index_label="Time [ms]", encoding='utf-8-sig')
            print(f"{file_name} の加算平均を {output_file} に保存しました。")

# Correct試行とError試行の加算平均を計算
calculate_grand_average(correct_dir, ave_output_dir, "correct")
calculate_grand_average(error_dir, ave_output_dir, "error")

# 比較用CSV作成
for electrode in electrodes:
    correct_file = os.path.join(correct_dir, f"{electrode}_correct.csv")
    error_file = os.path.join(error_dir, f"{electrode}_error.csv")
    if os.path.exists(correct_file) and os.path.exists(error_file):
        correct_data = pd.read_csv(correct_file, index_col=0)
        error_data = pd.read_csv(error_file, index_col=0)

        diff_data = error_data.mean(axis=1) - correct_data.mean(axis=1)

        combined_data = pd.DataFrame({
            "Time [ms]": correct_data.index,
            "Error Average [μV]": error_data.mean(axis=1).values,
            "Correct Average [μV]": correct_data.mean(axis=1).values,
            "Difference [μV]": diff_data.values
        })

        output_file = os.path.join(comp_output_dir, electrode, f"{electrode}_comp.csv")
        combined_data.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"{electrode} の比較用CSVを保存しました: {output_file}")
    else:
        print(f"{electrode} のデータが見つかりませんでした。")

print("全ての加算平均と比較CSVの作成が完了しました。")
