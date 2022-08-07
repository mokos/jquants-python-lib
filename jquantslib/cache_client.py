import re
import json
import datetime
from glob import glob

from .base_client import BaseClient
from .utils import local_chdir

class CacheClient(BaseClient):
    '''
    キャッシュ機能付き JQuants API クライアント
    
    # キャッシュする動機
    ・事前にデータ取得するコードを書く手間が省け、欲しいデータを都度取得するような実装にできる
    　(2回目以降は勝手にキャッシュを読み込む)
    ・たびたび分析を行いたい場合、APIアクセス回数を減らして効率Up
    ・上場株情報一覧など、タイミングにより変化するものについて、過去の時点の情報を残したい
    
    # 仕様
    APIのパス(例: /listed/info)ごとにディレクトリを作り、
    JSONデータをデータ取得日時のファイル名で保存します。
    
    基準日時(base_datetime)以降に取得された中で最も古いキャッシュを読み込みます。
    該当するキャッシュが存在しない場合は、APIからデータ取得しつつ現在時刻でキャッシュを作成します。
    
    # やらないこと
    一度キャッシュしたファイルの削除

    # 注意
    JQuants APIの契約期間の終了時、キャッシュはすべて手動で削除してください。
    また、キャッシュディレクトリは自身のみアクセスできる場所を設定してください。
    
    '''
    
    CACHE_NAME_TEMPLATE = 'YYYY-MM-DD HH:MI:SS.json'
    END_OF_BETA_TEST = datetime.date(2023, 3, 31)
    CACHE_GLOB_PATTERN = re.sub(r'[A-Z]', '[0-9]', CACHE_NAME_TEMPLATE)

    def __init__(self, *, refresh_token=None, cache_dir, base_datetime):
        if datetime.date.today()>self.END_OF_BETA_TEST:
            print('βテスト期間が終了しました。')
            print('これまで JQuants API から取得したデータをすべて削除してください。')
            raise

        self.cache_dir = cache_dir
        self.base_datetime = base_datetime

        super().__init__(refresh_token=refresh_token)
        
    def get_json(self, api_path):
        def cache_name(get_datetime):
            t = get_datetime.strftime('%Y-%m-%d %H:%M:%S')
            return self.CACHE_NAME_TEMPLATE.replace('YYYY-MM-DD HH:MI:SS', t)

        if api_path[0]!='/':
            raise
        
        with local_chdir(self.cache_dir + api_path, mkdir_if_not_exist=True):
            # 基準日時以降の最も古いキャッシュを探す
            base_cache_name = cache_name(self.base_datetime)
            for cached_name in sorted(glob(self.CACHE_GLOB_PATTERN)):
                if cached_name >= base_cache_name:
                    with open(cached_name) as f:
                        return json.load(f)
                    
            # 基準日時以降のキャッシュが見つからなかった場合
            # APIからデータを取得してキャッシュを作りつつjsonで返す
            j = super().get_json(api_path)
            
            # データ取得時刻でキャッシュを作成
            new_cache_name = cache_name(datetime.datetime.now())
            with open(new_cache_name, 'w') as f:
                json.dump(j, f)
            return j
    
