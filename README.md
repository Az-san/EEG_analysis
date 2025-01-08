# README

## このディレクトリについて
このディレクトリは、DAQ Masterで計測した脳波データから、Matlabで前処理を行い、その後Pythonを用いてタスク動作時の各TTL信号の-1〜2[s]間を1エポックとして切り出し、エポックをログデータ（ErrP、`robot_pkg/data`で生成されるbigmazeのログファイル）に基づいてError試行とCorrect試行に振り分けるスクリプトが保存されている。各エポックの電極の振幅を波形にするまでの一連の処理を行う。

---

## Matlabスクリプトについて
- `.ced`ファイルは存在しても、なくてもスクリプトは実行可能
- ICA処理したデータを`txt`ファイルに保存するまでは自動で処理される
- `txt`ファイルを`csv`に変換する作業は手動で行う

---

## Pythonスクリプトの使い方

### 電極の設定（`1_epoch.py`）
以下は初期設定。使用する電極に応じて自由に変更可能

設定している1〜5などの列番号は、`1_epoch.py`で読み込むICA処理済みデータ（CSVファイル）を指す。

```python
electrodes = {
    "F3": 1,
    "Fz": 2,
    "F4": 3,
    "FCz": 4,
    "Cz": 5
}
```

---

### デフォルトエポック数の設定（`1_epoch.py`）
以下は初期設定。タスクの試行時間と`EventTime`の回数に応じて自由に変更可能

```python
ttl_times_ms = raw_data.iloc[5:61, 9].astype(float).values * 1000  # 生データのTTLを[s]から[ms]に変換
```

初期設定では"Event Time"（生データの9列目）の5行目〜61行目、計57個のTTLから57個のエポックデータを算出している。

**注意:**
エポックを作成するために必要な時間の脳波データが足りていない場合（最後のTTLなど、TTL発信後2秒経つ前にそのタスクが終了した場合など）は、そのTTLをエポック作成対象から除外される。

---

## タスクのエラー率別のスクリプト実行方法

### Error試行ありの場合
以下の順番でスクリプトを実行すること。

1. `1_epoch.py`
2. `2_baseline.py`
3. `3_sort_err_new.py`
4. `colave.py`
5. `5_plot.py`

### Error試行なしの場合（`ros1_ws`の`MS_main.py`で`Errrate=0`に設定した場合）
以下の順番でスクリプトを実行すること。

1. `1_epoch_noerr.py`
2. `2_baseline.py`
3. `3_sort_err_noerr.py`
4. `colave.py`
5. `5_plot_noerr.py`

**注意:**
- `5_plot_noerr.py`ではCorrect波形しか生成されない。

---
