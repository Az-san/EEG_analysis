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
初期設定。使用する電極に応じて自由に変更可能

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
初期設定。タスクの試行時間と`EventTime`の回数に応じて自由に変更可能

```python
ttl_times_ms = raw_data.iloc[5:61, 9].astype(float).values * 1000  # 生データのTTLを[s]から[ms]に変換
```

初期設定では"Event Time"（生データの9列目）の5行目〜61行目、計57個のTTLから56個のエポックデータを算出する。

**注意:**
エポックを作成するために必要な時間の脳波データが足りていない場合（最後のTTLなど、TTL発信後2秒経つ前にそのタスクが終了した場合など）は、そのTTLをエポック作成対象から除外する。

---

## タスクのエラー率別のスクリプト実行方法

### サンプリング周波数1000Hz、エラー率10%試行の場合
以下の順番でスクリプトを実行する。

1. `1_epoch.py` - エポックの切り出し
2. `1_plot.py` - エポック波形プロット
3. `2_baseline.py` - ベースライン補正
4. `3_sort.py` - EpochをCorrect試行とError試行に振り分ける
5. `4_colave.py` - Correct試行とError試行のエポックの加算平均を計算
6. `5_plot.py` - `4_colave.py`で計算した加算平均をプロット

### サンプリング周波数1000Hz、エラーなし試行の場合
以下の順番でスクリプトを実行する。

1. `1_epoch_clean.py` - エポックの切り出し（Error試行なし）
2. `1_plot.py` - エポック波形プロット
3. `2_baseline.py` - ベースライン補正
4. `3_sort_clean.py` - Correct試行のみに基づいてEpochを振り分ける
5. `4_colave.py` - Correct試行のエポックの加算平均を計算
6. `5_plot_clean.py` - `4_colave.py`で計算したCorrect波形をプロット

### サンプリング周波数1024Hz（バンドパスフィルタ2-10Hz適用）の場合
以下の順番でスクリプトを実行する。

1. `0_before_10.py` - 事前処理
2. `1_epoch_10.py` - エポックの切り出し
3. `1_plot.py` - エポック波形プロット
4. `2_baseline.py` - ベースライン補正
5. `3_sort_10.py` - Epochの分類
6. `4_colave.py` - 加算平均の計算
7. `5_plot.py` - 波形のプロット

---

## `pkl_analysis.py` について
`pkl_analysis.py`は、ROSの迷路探索で得たシステムのpklデータ（`robot_pkg/data`にあるログファイル）を使用して、各エポックをCorrect試行とError試行に分類する。この際、`/log/pkl_analysis`ディレクトリ内に`combined_data.csv`が存在しないと、`3_sort.py`は正常に動作しない。

---

## スクリプト末尾の命名規則について
- `clean`：エラー試行なしバージョンに対応したスクリプト。例えば、`3_sort_clean.py`ではError試行に振り分ける必要がないため、Correct試行のみのCSVファイルを作成する。同様に、`5_plot_clean.py`ではError試行のグラフ生成を省略している。
- `10`：バンドパスフィルタリングを2-10Hzに適用したデータ解析用のスクリプト。元の2-40Hzフィルタデータと異なる計算手法が必要なため、専用のスクリプトとして作成されている。

---
