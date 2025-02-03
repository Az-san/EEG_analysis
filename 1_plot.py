#######################################################################################################
#  2024/12/23 作成
#  2025/01/06 改訂
#  2025/01/08 再改訂
#  2025/02/02 再々改訂（波形プロット部削除）
#
#  --1000Hz, エラーありセッション--
#  【1_epoch.pyの後に実行すること】
#
# 【概要】統合CSVデータから波形プロットを作成
# 各電極のエポックデータ（統合CSV）を読み込み、オリジナル波形およびズームイン波形をPNG形式で保存する
# TTL線の表示はオプションで切り替え可能。
#
# 【処理内容】
# 1. 統合CSV（"epoch_summary" ディレクトリ内）を読み込む
# 2. 各電極ごとにオリジナル波形（-1000ms～2000ms）をプロット
# 3. 各電極ごとにズームイン波形（-400ms～1000ms）をプロット
# 4. プロット画像をPNG形式で保存
#
# 【出力先】
# - "calc/plots/{電極名}/" にPNGファイルとして保存
#   - オリジナル波形: "epoch_{エポック番号}_original.png"
#   - ズームイン波形: "epoch_{エポック番号}_zoomed.png"
#######################################################################################################



import pandas as pd
import matplotlib.pyplot as plt
import os
from tkinter import Tk
from tkinter.filedialog import askdirectory

# TTL線の表示設定
SHOW_TTL = False  # TrueにするとTTL線が表示される

# GUIを使ったディレクトリ選択関数
def select_directory(prompt):
    print(prompt)
    Tk().withdraw()
    return askdirectory(title=prompt)

# 解析のルートディレクトリをユーザーに選択させる
root_dir = select_directory("解析のルートディレクトリを選択してください")
calc_dir = os.path.join(root_dir, "calc")
summary_output_dir = os.path.join(calc_dir, "epoch_summary")

# 電極リスト
electrodes = ["F3", "Fz", "F4", "FCz", "Cz"]

# 各電極の統合データを読み込み、波形プロットを作成
for electrode in electrodes:
    summary_csv_path = os.path.join(summary_output_dir, f"{electrode}_epoch_summary.csv")

    if os.path.exists(summary_csv_path):
        data = pd.read_csv(summary_csv_path)
        time = data["TIME"]

        # 各エポックのプロット
        for i in range(1, data.shape[1]):
            # オリジナルプロット
            plt.figure(figsize=(10, 6))
            plt.plot(time, data.iloc[:, i])
            if SHOW_TTL:
                plt.axvline(0, color='brown', linestyle='--')
            plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
            plt.axvline(0, color='black', linestyle='--', linewidth=0.8)
            plt.xticks(ticks=[-1000, -500, 0, 500, 1000, 1500, 2000], labels=["-1", "-0.5", "0", "0.5", "1", "1.5", "2"], fontsize=16)
            plt.yticks(fontsize=16)
            plt.title(f'{electrode} Epoch {i}', fontsize=20)
            plt.xlabel('Time [s]', fontsize=20)
            plt.ylabel('Amplitude [μV]', fontsize=20)
            plt.xlim(-1000, 2000)
            plt.ylim(-16, 16)

            plot_dir = os.path.join(calc_dir, "plots", electrode)
            os.makedirs(plot_dir, exist_ok=True)
            plt.savefig(os.path.join(plot_dir, f'epoch_{i}_original.png'), dpi=300)
            plt.close()

            # ズームインプロット
            plt.figure(figsize=(10, 6))
            plt.plot(time, data.iloc[:, i])
            if SHOW_TTL:
                plt.axvline(0, color='brown', linestyle='--')
            plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
            plt.axvline(0, color='black', linestyle='--', linewidth=0.8)
            plt.xticks(ticks=[-400, -200, 0, 200, 400, 600, 800, 1000], fontsize=16)
            plt.yticks(fontsize=16)
            plt.title(f'{electrode} Epoch {i}', fontsize=20)
            plt.xlabel('Time [ms]', fontsize=20)
            plt.ylabel('Amplitude [μV]', fontsize=20)
            plt.xlim(-400, 1000)  # ズームイン範囲
            plt.ylim(-16, 16)

            plt.savefig(os.path.join(plot_dir, f'epoch_{i}_zoomed.png'), dpi=300)
            plt.close()

        print(f"{electrode} のプロットを保存しました。")
    else:
        print(f"{summary_csv_path} が見つかりませんでした。")
