#######################################################################################################
#  2024/12/23 作成　
# 1. 生データ（.csv）とICA処理済みデータ（.csv）を選択する
#    - 生データにはTTL信号のタイミング情報が含まれている
#    - ICA処理済みデータには各電極の脳波データが含まれている
# 2. 各TTL信号のタイミングを基にエポックデータを生成する
#    - エポックはTTL信号を中心に、指定した時間範囲（-1秒から2秒）を切り出す
# 3. エポックデータを電極ごとにCSVファイルとして保存する
# 4. 各エポックの波形をプロットしてPNGファイルとして保存する
#    - 縦軸の範囲は-17μVから17μV
#    - 1μVごとに罫線を引き、5μVごとにラベルを表示する
# 5. すべてのエポックを統合したデータを電極ごとにCSVファイルとして保存する
#    - 統合データは"epoch_summary"ディレクトリに保存される
#
#　2024/12/26　サンプリング周波数変換用プログラムへ変更
#######################################################################################################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# GUIを使ったファイル選択関数
def select_file(prompt):
    print(prompt)  # ユーザーに選択を促すメッセージを表示
    Tk().withdraw()  # GUIウィンドウを非表示
    file_path = askopenfilename()  # ファイル選択ダイアログを表示
    return file_path

# 生データ（CSV）とICA処理済みデータ（TXT）のファイルを選択
raw_data_file = select_file("生データ（.csv）のファイルを選択してください。")
ica_data_file = select_file("ICA処理済みデータ（.csv）のファイルを選択してください。")

# データの読み込み
try:
    raw_data = pd.read_csv(raw_data_file, encoding='windows-1252')
    ica_data = pd.read_csv(ica_data_file, sep=r'\s+', header=None, encoding='shift-jis', low_memory=False)
    ica_data = ica_data.apply(pd.to_numeric, errors='coerce').dropna()
except Exception as e:
    print(f"データ読み込み中にエラーが発生しました: {e}")
    raise

# 電極と対応する列番号
electrodes = {
    "F3": 1,   # F3（チャネル1）
    "Fz": 2,   # Fz（チャネル2）
    "F4": 3,   # F4（チャネル3）
    "FCz": 4,  # FCz（チャネル4）
    "Cz": 5    # Cz（チャネル5）
}

# 時間データとTTL信号の取得
time_data = ica_data.iloc[:, 0].values  # 時間データ（列0）
ttl_times = raw_data.iloc[4:61, 9].astype(float).values  # TTL信号のタイミング

# TTL信号がデータ範囲内か確認
max_time = time_data[-1]
valid_ttl_times = [ttl for ttl in ttl_times if ttl + 2.0 <= max_time / 1000]

# エポック範囲とサンプリング設定
epoch_start = -1.0  # 開始時間（秒）
epoch_end = 2.0  # 終了時間（秒）
original_sampling_rate = 1000  # 元のサンプリング周波数（Hz）
new_sampling_rate = 1024  # 新しいサンプリング周波数（Hz）
num_samples = int((epoch_end - epoch_start) * new_sampling_rate)  # 新しいサンプリング数

# TTL信号の補正
# TTLのタイミングを新しいサンプリング周波数に変換
corrected_ttl_times = [
    round(ttl * (new_sampling_rate / original_sampling_rate), 6)
    for ttl in valid_ttl_times
]

# 各電極の統合データを保持する辞書
epoch_summary_data = {electrode: [] for electrode in electrodes.keys()}

# エポック処理
for electrode, col_idx in electrodes.items():
    electrode_dir = f"epoch_data_{electrode}_{new_sampling_rate}Hz"
    os.makedirs(electrode_dir, exist_ok=True)

    electrode_data = ica_data.iloc[:, col_idx].values  # 電極データを取得

    for i, ttl in enumerate(corrected_ttl_times):
        try:
            # エポック範囲をミリ秒単位で計算
            start_time = ttl + epoch_start
            end_time = ttl + epoch_end

            # インデックス計算
            start_idx = np.searchsorted(time_data / 1000, start_time)
            end_idx = np.searchsorted(time_data / 1000, end_time)

            if end_idx - start_idx != num_samples:
                print(f"{electrode} - エポック {i+1}: サンプル数が不足しています。補完なしで続行します。")
                continue

            # エポックデータを切り出し
            epoch_data = electrode_data[start_idx:end_idx]
            epoch_time = np.linspace(epoch_start, epoch_end, num_samples)  # 時間を均等分割

            # エポックデータを保存
            csv_path = os.path.join(electrode_dir, f'epoch_{i+1}_{electrode}_{new_sampling_rate}Hz.csv')
            epoch_df = pd.DataFrame({
                'Time [s]': epoch_time,
                'Amplitude [μV]': epoch_data
            })
            epoch_df.to_csv(csv_path, index=False, encoding='utf-8-sig')

            # 波形プロット
            plt.figure(figsize=(10, 5))
            plt.plot(epoch_time, epoch_data, label=f'TTL {i+1}')
            plt.axvline(x=0, color='brown', linestyle='--', label='TTL Signal')
            plt.axvline(x=epoch_start, color='blue', linestyle='--', label='Epoch Start')
            plt.axvline(x=epoch_end, color='green', linestyle='--', label='Epoch End')

            x_ticks = np.arange(epoch_start, epoch_end + 0.5, 0.5)
            plt.xticks(ticks=x_ticks, labels=[f"{tick:.3f}" for tick in x_ticks])
            plt.title(f'{electrode} Epoch for TTL {i+1}')
            plt.xlabel('Time [s]')
            plt.ylabel('Amplitude [μV]')
            plt.yticks(np.arange(-17, 18, 5))
            plt.grid(which='major', linestyle='-', linewidth=0.5)
            plt.grid(which='minor', linestyle=':', linewidth=0.5)
            plt.minorticks_on()

            # プロットを保存
            plot_path = os.path.join(electrode_dir, f'epoch_{i+1}_{electrode}_{new_sampling_rate}Hz.png')
            plt.savefig(plot_path, dpi=300)
            plt.close()

            # 統合データに追加
            epoch_summary_data[electrode].append(epoch_data)

        except Exception as e:
            print(f"{electrode} - エポック {i+1} の処理中にエラーが発生しました: {e}")

# 統合データの保存
summary_output_dir = f"epoch_summary_{new_sampling_rate}Hz"
os.makedirs(summary_output_dir, exist_ok=True)

for electrode, data in epoch_summary_data.items():
    if data:
        summary_df = pd.DataFrame(np.array(data).T)
        summary_df.columns = [f"Epoch {i+1}" for i in range(summary_df.shape[1])]
        summary_csv_path = os.path.join(summary_output_dir, f"{electrode}_epoch_summary_{new_sampling_rate}Hz.csv")
        summary_df.to_csv(summary_csv_path, index=False, encoding='utf-8-sig')
        print(f"{electrode} の統合データを {summary_csv_path} に保存しました。")

print("すべての処理が完了しました。")
