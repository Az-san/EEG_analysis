#######################################################################################################
#  2025/01/15 作成
#
#  --1024Hz用, 2-10Hzフィルタ版--
#  【エポック切り出し前処理プログラム】
#  【1_epoch_10.pyの前に実行すること】
#
# 【概要】ICA処理済みデータの前処理
# 生データとICA処理済みデータから、TTL信号を基準にエポック切り出しのための前処理を行う。
# このプログラムでは、ICAデータの補間やサンプリングレート調整を行い、1024Hz対応のデータに変換する。
#
# 【処理内容】
# 1. 生データ（raw_data.csv）とICA処理済みデータ（ica_data.csv）をGUIで選択
# 2. TTL信号（生データ9列目）に基づき、データ範囲を確認
# 3. ICA処理済みデータを1ms間隔に補間してサンプリングレートを1024Hzに変換
# 4. 補間後のデータをCSV形式で保存
#
# 【出力先】
# - 前処理後のデータ: "/2-10Hz_1ms.csv" として保存
#
# 【注意】
# - 生データ: CSV形式、"windows-1252"エンコーディング
# - ICAデータ: CSV形式、"utf-8"エンコーディング
# - TTL信号が-1000ms〜+2000msの範囲内であることを確認
#######################################################################################################


import pandas as pd
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# ✅ GUIを使ったファイル選択関数
def select_file(prompt):
    print(prompt)
    Tk().withdraw()
    return askopenfilename(title=prompt)

# ✅ ICA処理済みデータのファイルを選択
ica_data_file = select_file("ICA処理済みデータ（.csv）のファイルを選択してください。")

# ✅ データの読み込み
try:
    ica_data = pd.read_csv(ica_data_file)
except Exception as e:
    print(f"データ読み込み中にエラーが発生しました: {e}")
    raise

# ✅ 元のTime列を取得
time_data = ica_data.iloc[:, 0].values  # Time列の取得

# ✅ 新しい1ms間隔のTime列を作成
new_time_data = np.arange(time_data[0], time_data[-1], 0.001)  # 1ms間隔

# ✅ 新しいTime列に対して各電極データを補間
electrodes = ica_data.columns[1:]  # 電極名の取得
new_ica_data = pd.DataFrame({"Time [s]": new_time_data})

for electrode in electrodes:
    new_ica_data[electrode] = np.interp(new_time_data, time_data, ica_data[electrode].values)

# ✅ 新しいCSVファイルとして保存
output_file = ica_data_file.replace(".csv", "_1ms.csv")
new_ica_data.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"1ms間隔の補間データを {output_file} に保存しました。")
