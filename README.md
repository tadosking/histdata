# histdataのローダー
フリーのFX過去データのダウンロードサイト「histdata.com」のデータをpandas DataFrameで使えるようにしました。

## 使い方

### 準備

フリーのFXレート配信サイト「histdata.com」(https://www.histdata.com)へアクセスし、ASCII M1データをダウンロード&解凍して好きなディレクトリにまとめて突っ込んでおきます。

```
tadosking@MacBook-Pro-2 sample_data % ls /Users/tadosking/dev/fin/histdata/sample_data 
DAT_ASCII_EURUSD_M1_2021.csv	DAT_ASCII_EURUSD_M1_202302.csv
DAT_ASCII_EURUSD_M1_2022.csv	DAT_ASCII_USDJPY_M1_2022.csv
DAT_ASCII_EURUSD_M1_202301.csv	DAT_ASCII_USDJPY_M1_202301.csv
```

また、config.yamlを開いて、`histdata_dir`を書き換えます。

### 基本的な使い方

```
from histdata_loader import HistdataLoader
loader = HistdataLoader()
df = loader.load('USDJPY', '1d', start='2020-1-1', end='2020-1-15)
```

### 別の設定ファイルを使いたいとき

デフォルトの`config.yaml`をコピって自分専用の設定ファイルにすることもできます。

```
loader = HistdataLoader(config_path='どこか/my_config.yaml')
```

### ローソク足の時間軸を変更したいとき

'1w', '1d', '8h', '4h', '3h', '1h', '30min', '15min', '5min' が指定できます。
他のローソク足を使いたい場合は`config.yaml`をいじってください。

```
df = loader.load('EURUSD', '4h')
```

### タイムゾーンを変更したいとき

デフォルトではN.Yでの日付時刻で返しますが、東京での日付時刻で欲しい場合など。

```
df = loader.load('USDJPY', '1d', timzone='Asia/Tokyo')
```
