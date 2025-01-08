このディレクトリは、DAQ Masterで計測した脳波データから、Matlabで前処理を行い、その後Pythonを用いてタスク動作時の各TTL信号-1~2[s]間を1エポックとして切り出し、エポックをログデータ（ErrP, robot_pkg/dataで生成されるbigmazeのログファイル）に基づいてerror試行とcorrect試行に振り分け、その間の電極の振幅を波形にするまでの一連のPythonスクリプトを保存している。


### Matlabスクリプトについて
・cedファイルはあってもなくても実行できるかと
・ICA処理したデータをtxtファイルに保存するまでは自動。txtファイルをcsvに変換する作業は手動


### Pythonスクリプトの使い方

## 電極（1_epoch.py）
以下は初期設定。使用した電極に応じて自由に変更可能
設定している1~5などの列番号は、<1_epoch.py>で読み込むICA処理済みデータ（csvファイル）
electrodes = {
    "F3": 1,
    "Fz": 2,
    "F4": 3,
    "FCz": 4,
    "Cz": 5
}

## デフォルトエポック数（1_epoch.py）
以下は初期設定。タスクの試行時間とEventTimeの回数に応じて自由に変更可能

ttl_times_ms = raw_data.iloc[5:61, 9].astype(float).values * 1000  # 生データのTTLを[s]から[ms]に変換

初期設定では"Event Time"（生データ9列目）5行目-61行目、計57個のTTLから57個のエポックデータを算出している。
エポックを作成するに必要な時間の脳波データが足りてない場合（最後のTTLなど, TTL発信後2秒立つ前にそのタスクが終了された場合など）は、そのTTLをエポック作成対象には入れない。


## Error試行ありの場合
１）1_epoch.py
２）2_baseline.py
３）3_sort_err_new.py
４）colave.py
５）5_plot.py
の順番で実行


## Error試行なしの場合（ros1_wsのMS_main.pyでErrrate=0にした場合）
１）1_epoch_noerr.py
２）2_baseline.py
３）3_sort_err_noerr.py
４）colave.py
５）5_plot_noerr.py
の順番で実行

※５）ではCorrect波形しか生成されない

