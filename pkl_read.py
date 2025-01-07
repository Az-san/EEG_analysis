import os
import pickle
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askdirectory

# このプログラムのプロトコル:
# 1. 指定されたディレクトリ内のすべての.pklファイルを検索する。
# 2. 各.pklファイルの内容をデコードしてテキスト形式またはCSV形式で保存する。
# 3. ファイル名ごとに内容を分類し、それがどのようなデータを含むかを解析できるようにする。

# GUIを使ったディレクトリ選択関数
def select_directory(prompt):
    print(prompt)  # ユーザーに選択を促すメッセージを表示
    Tk().withdraw()  # GUIウィンドウを非表示
    directory = askdirectory()  # ディレクトリ選択ダイアログを表示
    return directory

# ログファイルが保存されているディレクトリを選択
input_dir = select_directory("ログデータが保存されているディレクトリを選択してください。")
output_dir = select_directory("解析結果を保存するディレクトリを選択してください。")
os.makedirs(output_dir, exist_ok=True)

# 指定ディレクトリ内のすべての.pklファイルを取得
pkl_files = [f for f in os.listdir(input_dir) if f.endswith('.pkl')]

for pkl_file in pkl_files:
    pkl_path = os.path.join(input_dir, pkl_file)
    output_txt_path = os.path.join(output_dir, f"{os.path.splitext(pkl_file)[0]}.txt")

    try:
        # .pklファイルを読み込み
        with open(pkl_path, 'rb') as file:
            data = pickle.load(file)

        # データをテキスト形式に変換して保存
        with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
            if isinstance(data, dict):
                for key, value in data.items():
                    txt_file.write(f"{key}: {value}\n")
            elif isinstance(data, list):
                for item in data:
                    txt_file.write(f"{item}\n")
            else:
                txt_file.write(str(data))

        print(f"{pkl_file} の内容を {output_txt_path} に保存しました。")

    except Exception as e:
        print(f"{pkl_file} の読み込み中にエラーが発生しました: {e}")

print("すべての.pklファイルの内容を保存しました。")
