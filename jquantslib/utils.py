import os

class local_chdir:
    '''
    一時的にディレクトリに移動するため、with構文でのみ使います。
    '''
    
    def __init__(self, dir_path, mkdir_if_not_exist=False):
        self.dir_path = dir_path
        self.mkdir_if_not_exist = mkdir_if_not_exist
        
    def __enter__(self):
        self.orig_path = os.getcwd()
        
        if self.mkdir_if_not_exist:
            os.makedirs(self.dir_path, exist_ok=True)
            
        os.chdir(self.dir_path)
        
    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.orig_path)
