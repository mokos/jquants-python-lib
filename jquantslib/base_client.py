import os
import requests
import pandas as pd
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

class BaseClient:
    '''
    JQuants API クライアント

    # リフレッシュトークンの設定方法(上から優先)
    - 初期化時にrefresh_tokenパラメータに渡す
    - 環境変数 JQUANTS_REFRESH_TOKEN に設定しておく
    
    # 役割
    有効なリフレッシュトークンの設定がされていれば、
    APIからデータを取得し JSON や pandas.DataFrame で返すことができる。
    
    # やらないこと
    - リフレッシュトークンの取得
    - APIから取得したデータの加工(DataFrameにする程度まではやる)
    
    '''
    
    BASE_URL = 'https://api.jpx-jquants.com/v1'
    ID_TOKEN_URL = BASE_URL + '/token/auth_refresh?refreshtoken={refreshtoken}'
    
    def __init__(self, *, refresh_token=None, timeout=30, retry_num=3):
        self.refresh_token = refresh_token or os.getenv('JQUANTS_REFRESH_TOKEN')
        if self.refresh_token is None:
            print('please set refresh token')
            raise

        self.timeout = timeout
        self.retry_num = retry_num
        self.id_token = None

    def reset_id_token(self):
        self.id_token = None
        
    def get_id_token(self):
        if self.id_token is None:
            url = self.ID_TOKEN_URL.format(refreshtoken=self.refresh_token)
            res = requests.post(url)
            res.raise_for_status()
            self.id_token = res.json()['idToken']
            
        return self.id_token
    
    def make_headers(self):
        return { 'Authorization': f'Bearer {self.get_id_token()}' }
    
    def make_session(self):
        session = requests.Session()
        
        # リトライの設定
        retries = Retry(total=self.retry_num
                        , backoff_factor=1
                        , status_forcelist=[429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        
        return session
        
    def get_response(self, api_path):
        url = self.BASE_URL + api_path
        session = self.make_session()
        res = session.request('GET', url, timeout=self.timeout, headers=self.make_headers())

        # 401エラー(Unauthorized)の場合、IDトークンが期限切れの可能性が高い。
        # 既存のIDトークンをリセットしてリトライ
        if res.status_code == 401:
            print('maybe ID token has expired. reset old ID token.')
            self.reset_id_token()
            res = session.request('GET', url, timeout=self.timeout, headers=self.make_headers())

        res.raise_for_status()
        return res
    
    def get_json(self, api_path):
        return self.get_response(api_path).json()
    
    def get_json_data_part(self, api_path):
        j = self.get_json(api_path)
        keys = list(j.keys())
        
        # APIから取得できるデータは、
        # { "someKey" : データの中身 } のようなJSONになっていて、
        # キー名は特に用途がないため、初めからデータの中身のみを返す

        if len(keys)!=1:
            raise # 仕様変更を検知するため
            
        return j[keys[0]]
    
    def get_df(self, api_path):
        return pd.DataFrame(self.get_json_data_part(api_path))
    
