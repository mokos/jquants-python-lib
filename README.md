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
```
client = jq.BaseClient(refresh_token=YOUR_TOKEN)

# API /listed/info の結果をJSONで取得
print(client.get_json('/listed/info'))

# API /listed/info の結果をJSONからDataFrameに変換して取得
print(client.get_df('/listed/info'))

```

## CacheClient
CacheClientは、基準日時(base_datetime)以降に取得したキャッシュがあれば、キャッシュから読み込みます。

また、CacheClientがAPIから取得したデータを自動でキャッシュします。

キャッシュを保存するディレクトリを cache_dir で指定します。

過去の期間の分析を繰り返したい場合などに、base_datetimeを固定すると、データ取得の時間を節約できます。

```
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

# 未実装
## IDトークン期限切れ対応
できれば24時間固定でなく、返ってくるエラーの種類で判定したい

現状は、IDトークンが期限切れたらクライアント作り直してください


# 注意事項
JQuants API の利用規約に従って、ご自身の責任にて利用してください。
