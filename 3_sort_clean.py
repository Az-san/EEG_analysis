#############################################################################################
#  2024/12/23 作成
#  2025/01/06 改訂
#
#  --1000Hz, エラーなしセッション用--
# 【2_baseline.pyの後に実行すること】
#
# 【概要】Correct試行の分類（Error試行なし）
# エポックデータをCorrect試行に分類し、データを"calc/correct"ディレクトリに保存する。
#
# 【処理内容】
# 1. "baseline"ディレクトリ内の各電極のエポックデータを読み込み
# 2. "log/pkl_analysis_noerror/combined_data.csv"の「ErrP」ラベル（0: Correct）に基づいて分類
# 3. 分類結果を"calc/correct"に保存（ファイル名: "{電極名}_correct.csv"）
#
# 【出力先】
# - Correct試行: "calc/correct"
#
# 【事前準備】
# - "log/pkl_analysis_noerror/combined_data.csv"をpkl_analysis.pyで作成しておくこと
#############################################################################################

import pandas as pd
import os
from tkinter.filedialog import askdirectory

# GUIで解析のルートディレクトリを選択
root_dir = askdirectory(title="解析のルートディレクトリを選択してください")

# ベースライン補正後のエポックデータのディレクトリ設定
epoch_dir = os.path.join(root_dir, "calc", "baseline")

# 出力先ディレクトリの設定
output_correct_dir = os.path.join(root_dir, "calc", "correct")
os.makedirs(output_correct_dir, exist_ok=True)

# 電極リスト
electrodes = ["Cz", "F3", "F4", "FCz", "Fz"]

# ラベル情報の読み込み
combined_data_path = os.path.join(root_dir, "log", "pkl_analysis_noerror", "combined_data.csv")

# ファイル存在チェック
if not os.path.isfile(combined_data_path):
    raise FileNotFoundError(f"combined_data.csv が見つかりません: {combined_data_path}")

combined_df = pd.read_csv(combined_data_path)

# Correct試行のエポックを分類
correct_epochs = combined_df[combined_df["ErrP"] == 0]["Epoch"].astype(int).astype(str).tolist()

# 各電極のエポックデータを分類して保存
for electrode in electrodes:
    try:
        # エポックデータの読み込み
        electrode_file = os.path.join(epoch_dir, f"{electrode}_epoch_base.csv")
        if not os.path.isfile(electrode_file):
            print(f"{electrode} のエポックデータが見つかりません: {electrode_file}")
            continue

        electrode_data = pd.read_csv(electrode_file, index_col=0)

        # 存在するエポック番号のみ抽出
        valid_correct_epochs = [epoch for epoch in correct_epochs if epoch in electrode_data.columns]

        # Correct試行データの抽出と保存
        correct_data = electrode_data.loc[:, valid_correct_epochs]
        correct_file = os.path.join(output_correct_dir, f"{electrode}_correct.csv")
        correct_data.to_csv(correct_file, index=True, encoding='utf-8-sig')
        print(f"{electrode} の Correct試行データを保存しました: {correct_file}")

    except Exception as e:
        print(f"{electrode} のデータ処理中にエラーが発生しました: {e}")

print("すべてのエポックデータを分類して保存しました。")
