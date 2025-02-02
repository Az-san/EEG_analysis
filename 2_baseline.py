#############################################################################################
#  2024/12/23 作成
#  2025/01/06 改訂
#
# --Errorありなし共通, サンプリング周波数共通--
# 【1_epoch.py, 1_epoch_clean.py, 1_epoch_10.pyの後に実行すること】
#
# 【概要】ベースライン補正
# "epoch_summary" 内のエポックデータを読み込み、ベースライン補正後のデータを "calc/baseline" に保存する。
#
# 【処理内容】
# 1. "epoch_summary" 内の各電極のエポックデータ（CSV）を読み取り
# 2. -1000msから0msまでの平均値をベースラインとして算出
# 3. 各エポックデータからベースライン値を減算して補正
# 4. 補正後のデータを "calc/baseline" に保存（形式: "{電極名}_base.csv"）
# 5. 各電極のベースライン値を "baseline_values.csv" にまとめて保存
#
# 【出力先】
# - calc/baseline/
#   ├── Cz_base.csv
#   ├── F3_base.csv
#   ├── F4_base.csv
#   ├── FCz_base.csv
#   └── Fz_base.csv
# - calc/baseline/baseline_values.csv
#############################################################################################

import pandas as pd
import numpy as np
import os
from tkinter import Tk
from tkinter.filedialog import askdirectory

# GUIを使ったディレクトリ選択
def select_directory(prompt):
    print(prompt)
    Tk().withdraw()
    return askdirectory(title=prompt)

# 解析のルートディレクトリをユーザーに選択させる
root_dir = select_directory("解析のルートディレクトリを選択してください")
calc_dir = os.path.join(root_dir, "calc")

# 入力・出力ディレクトリの設定
input_dir = os.path.join(calc_dir, "epoch_summary")
output_dir = os.path.join(calc_dir, "baseline")
os.makedirs(output_dir, exist_ok=True)

# ベースライン補正値を記録するリスト
baseline_values = []

# "calc/epoch_summary" 内のCSVファイルを取得
csv_files = [f for f in os.listdir(input_dir) if f.endswith("_epoch_summary.csv")]

for file_name in csv_files:
    file_path = os.path.join(input_dir, file_name)

    # CSVファイルをロード
    data = pd.read_csv(file_path)

    # "Time [ms]"列を除外し、エポックデータを処理
    epochs_data = data.iloc[:, 1:]

    # -1000msから0msのデータを抽出
    baseline_range = epochs_data.iloc[:1000, :]

    # ベースライン値の計算
    baseline_value = baseline_range.mean(axis=1).mean()

    # ベースライン補正値を記録
    electrode_name = file_name.replace("_epoch_summary.csv", "")
    baseline_values.append({"Electrode": electrode_name, "Baseline Value": baseline_value})

    print(f"{file_name} のベースライン補正値: {baseline_value}")

    # ベースライン補正
    baseline_corrected_data = epochs_data - baseline_value
    baseline_corrected_data.insert(0, "Time [ms]", data["Time [ms]"])  # "Time [ms]"列を復元

    # 補正後のデータを保存
    output_file_path = os.path.join(output_dir, f"{electrode_name}_base.csv")
    baseline_corrected_data.to_csv(output_file_path, index=False, encoding='utf-8-sig')

    print(f"{file_name} のベースライン補正後のデータを保存しました: {output_file_path}")

# ベースライン補正値をCSVに保存
baseline_values_df = pd.DataFrame(baseline_values)
baseline_values_file_path = os.path.join(output_dir, "baseline_values.csv")
baseline_values_df.to_csv(baseline_values_file_path, index=False, encoding='utf-8-sig')

print(f"ベースライン補正値を保存しました: {baseline_values_file_path}")
