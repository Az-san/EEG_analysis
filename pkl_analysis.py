import pandas as pd
import os

# ファイルパスの設定
base_dir = r"C:\Users\Maiko Kudo\Documents\【IMPORTANT DATA】\脳波測定実験データ_DAQMaster"
combined_data_path = os.path.join(base_dir, "log", "pkl_analysis", "combined_data.csv")
epoch_dir = os.path.join(base_dir, "epoch_correction")

# 電極名
electrodes = ["Cz", "F3", "F4", "FCz", "Fz"]

# combined_dataの読み込み
combined_df = pd.read_csv(combined_data_path)

# Correct試行とError試行のエポックを分類
correct_epochs = combined_df[combined_df["ErrP"] == 0]["Epoch"].astype(str).tolist()
error_epochs = combined_df[combined_df["ErrP"] == 1]["Epoch"].astype(str).tolist()

# 加算平均を保存するためのデータフレーム
correct_average = pd.DataFrame()
error_average = pd.DataFrame()

# 電極ごとに処理
for electrode in electrodes:
    # 各電極のデータを読み込む
    electrode_file = os.path.join(epoch_dir, f"{electrode}_epoch_corrected.csv")
    electrode_data = pd.read_csv(electrode_file, index_col=0)  # インデックスに時間軸（ms）

    # インデックスを確認
    print(f"{electrode} Electrode Data Index Sample:")
    print(electrode_data.index[:5])

    try:
        # インデックスをエポック番号形式に変換 (必要に応じて調整)
        electrode_data.index = ["Epoch " + str(i + 1) for i in range(len(electrode_data))]
        
        # Correct試行のデータを抽出し、平均を計算
        correct_data = electrode_data.loc[["Epoch " + epoch for epoch in correct_epochs if "Epoch " + epoch in electrode_data.index]]
        correct_mean = correct_data.mean(axis=0)
        correct_average[electrode] = correct_mean

        # Error試行のデータを抽出し、平均を計算
        error_data = electrode_data.loc[["Epoch " + epoch for epoch in error_epochs if "Epoch " + epoch in electrode_data.index]]
        error_mean = error_data.mean(axis=0)
        error_average[electrode] = error_mean

    except KeyError as e:
        print(f"{electrode} - 試行データ処理中にエラー: {e}")

# Correct試行の平均結果を保存
correct_average_file = os.path.join(base_dir, "correct_average.csv")
correct_average.to_csv(correct_average_file, encoding="utf-8-sig")
print(f"Correct試行の平均結果を保存しました: {correct_average_file}")

# Error試行の平均結果を保存
error_average_file = os.path.join(base_dir, "error_average.csv")
error_average.to_csv(error_average_file, encoding="utf-8-sig")
print(f"Error試行の平均結果を保存しました: {error_average_file}")
