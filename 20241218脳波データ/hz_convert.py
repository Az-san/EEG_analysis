import pandas as pd
import numpy as np
import os
from scipy.interpolate import interp1d
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# GUIを使ったファイル選択関数
def select_file(prompt):
    print(prompt)  # ユーザーに選択を促すメッセージを表示
    Tk().withdraw()  # GUIウィンドウを非表示
    file_path = askopenfilename()  # ファイル選択ダイアログを表示
    return file_path

# ICA処理済みデータを選択
ica_data_file = select_file("1024HzのICA処理済みデータ（.csv）を選択してください。")

# データの読み込み
try:
    ica_data = pd.read_csv(ica_data_file, encoding='shift-jis')  # ヘッダーをそのまま読む
    # 1行目をヘッダーとして設定
    ica_data.columns = ica_data.iloc[0]
    ica_data = ica_data.drop(0).reset_index(drop=True)

    # 時間データを抽出
    original_time = ica_data.iloc[:, 0].astype(float).values
    ica_data = ica_data.drop(ica_data.columns[0], axis=1)  # 時間列をデータから削除
    ica_data = ica_data.apply(pd.to_numeric, errors='coerce')  # 数値変換
except Exception as e:
    print(f"データ読み込み中にエラーが発生しました: {e}")
    raise

# 出力先ディレクトリを作成
output_dir = "1000Hz_corrected_data"
os.makedirs(output_dir, exist_ok=True)

# 新しい時間軸（1000Hzの間隔）
target_time = np.linspace(original_time[0], original_time[-1], len(original_time) * 1000 // 1024)

# 各電極のデータを補間して保存
for electrode in ica_data.columns:
    try:
        electrode_data = ica_data[electrode].values  # 元データの振幅

        # 線形補間を適用
        interpolator = interp1d(original_time, electrode_data, kind='linear', bounds_error=False, fill_value="extrapolate")
        interpolated_amplitude = interpolator(target_time)

        # 新しいデータフレームを作成
        corrected_df = pd.DataFrame({
            'Time [ms]': target_time * 1000,  # 秒単位からミリ秒単位に戻す
            'Amplitude [μV]': interpolated_amplitude
        })

        # CSVファイルに保存
        output_file = os.path.join(output_dir, f"{electrode}_1000Hz_corrected.csv")
        corrected_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"{electrode} のデータを1000Hzに変換して保存しました: {output_file}")

    except Exception as e:
        print(f"{electrode} のデータ処理中にエラーが発生しました: {e}")

print("すべての電極データを補間して保存しました。")
