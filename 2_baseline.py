#############################################################################################
#  2024/12/23 作成
#  2025/01/06 改訂
#
# 【1_epoch.pyの後に実行すること！】
#
# 【概要】ベースライン補正
# "epoch_summary" ディレクトリ内のエポックデータを読み込み、ベースライン補正を実施して、補正後のデータを "calc/baseline" に保存する。
#
# 【処理内容】
# 1. "epoch_summary" 内の各電極のエポックデータ（CSVファイル）を読み取る
# 2. 各エポックの第2行目から第1001行目までの平均を計算し、それをベースライン値とする
# 3. 計算したベースライン値を全エポックデータから減算し、ベースライン補正を実施する
# 4. 補正後のエポックデータを新しいCSVファイルとして "calc/baseline" に保存する
#    - ファイル形式: "{電極名}_base.csv"
# 5. 各電極のベースライン補正値を "baseline_values.csv" にまとめて保存する
#
# 【出力先ディレクトリ】
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

# ✅ GUIを使ったディレクトリ選択
def select_directory(prompt):
    print(prompt)
    Tk().withdraw()
    return askdirectory(title=prompt)

# ✅ 解析のルートディレクトリをユーザーに選択させる
root_dir = select_directory("解析のルートディレクトリを選択してください")
calc_dir = os.path.join(root_dir, "calc")

# ✅ 入力・出力ディレクトリの設定
input_dir = os.path.join(calc_dir, "epoch_summary")
output_dir = os.path.join(calc_dir, "baseline")
os.makedirs(output_dir, exist_ok=True)

# ✅ ベースライン補正値を記録するリスト
baseline_values = []

# ✅ "calc/epoch_summary" ディレクトリ内のCSVファイルを取得
csv_files = [f for f in os.listdir(input_dir) if f.endswith("_epoch_summary.csv")]

for file_name in csv_files:
    file_path = os.path.join(input_dir, file_name)

    # ✅ CSVファイルをロード
    data = pd.read_csv(file_path)

    # ✅ カラム名を修正 (Epoch 1, Epoch 2, ... -> 1, 2, ...)
    new_columns = [str(i + 1) if col.startswith("Epoch") else col for i, col in enumerate(data.columns)]
    data.columns = new_columns

    # ✅ 各エポックの2行目から1001行目（0インデックスでは1から1000）の平均を計算
    epoch_means = data.iloc[1:1001, :].mean()

    # ✅ エポックごとの平均値を加算して、全体の平均を計算
    baseline_value = epoch_means.mean()

    # ✅ ベースライン補正値を記録
    electrode_name = file_name.replace("_epoch_summary.csv", "")
    baseline_values.append({"Electrode": electrode_name, "Baseline Value": baseline_value})

    print(f"{file_name} のベースライン補正値: {baseline_value}")

    # ✅ ベースライン補正を実施
    baseline_corrected_data = data - baseline_value

    # ✅ 補正後のデータを新しいCSVファイルとして保存
    output_file_path = os.path.join(output_dir, f"{electrode_name}_epoch_base.csv")
    baseline_corrected_data.to_csv(output_file_path, index_label="Epoch", encoding='utf-8-sig')

    print(f"{file_name} のベースライン補正後のデータを保存しました: {output_file_path}")

# ✅ ベースライン補正値をCSVファイルに保存
baseline_values_df = pd.DataFrame(baseline_values)
baseline_values_file_path = os.path.join(output_dir, "baseline_values.csv")
baseline_values_df.to_csv(baseline_values_file_path, index=False, encoding='utf-8-sig')

print(f"ベースライン補正値を保存しました: {baseline_values_file_path}")


