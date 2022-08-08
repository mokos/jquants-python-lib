# jquantslib
Python から J-Quants API を利用するライブラリ

# インストール
```
pip install git+https://github.com/mokos/jquants-python-lib
```

# 使い方
## リフレッシュトークンの設定
上から順に優先度高
1. クライアント作成時の引数 refresh_token
2. 環境変数 JQUANTS_REFRESH_TOKEN

## BaseClient
APIのデータを取得するためのシンプルなクライアント。

リフレッシュトークンが設定してあれば、自動でIDトークンを取得してデータを取得できます。

IDトークンが期限切れした場合も自動で再取得します。


```python
client = jq.BaseClient(refresh_token=YOUR_TOKEN)

# API /listed/info の結果をJSONで取得
print(client.get_json('/listed/info'))

# API /listed/info の結果をJSONからDataFrameに変換して取得
print(client.get_df('/listed/info'))

```

## CacheClient
BaseClientを継承したキャッシュ機能付きのクライアント。
　
- CacheClientがAPIから取得したデータを自動でキャッシュします。
- 基準日時以降に取得したキャッシュがあれば、キャッシュから読み込みます。

base_datetime: 基準日時(これ以降に取得されたキャッシュを利用する)

cache_dir: キャッシュを保存するディレクトリ

過去の期間の分析を繰り返したい場合などに、base_datetimeを固定すると、データ取得の時間を節約できます。

### date引数のAPIデータのキャッシュについて
date引数のAPI(たとえば /prices/daily_quates?date=2022-02-22)については、その日付からある程度時間が経過してから取得した場合、もうデータが変わることがないので、遠い未来(9999年1月1日)に取得したものとしてキャッシュを保存します。

現状では、引数の日付から次の日に日が変わってから24時間を経過している場合に、もうデータが変わることがないと判断しています。


```python
import jquantslib as jq

# 基準日時以降に取得したキャッシュを使うクライアントの作成
t = datetime.datetime(2022, 8, 6)
d = './cache'

client = jq.CacheClient(refresh_token=YOUR_TOKEN, cache_dir=d, base_datetime=t)

# 一度目は数秒かかる
print(client.get_df('/listed/info'))

# 二度目はキャッシュを読むので速い
print(client.get_df('/listed/info'))
```

# 注意事項
JQuants API の利用規約に従って、ご自身の責任にて利用してください。
