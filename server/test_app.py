#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app

print('=== アプリケーションテスト開始 ===')

try:
    with app.test_client() as client:
        print('テストクライアント作成成功')
        
        # 基本的なヘルスチェック
        print('ヘルスチェック中...')
        
        # 記事生成APIテスト
        print('記事生成APIテスト中...')
        response = client.post('/api/generate', json={
            'keyword': 'test', 
            'model': 'claude', 
            'includeImages': False, 
            'factCheck': False
        })
        
        print(f'ステータスコード: {response.status_code}')
        
        if response.status_code != 200:
            print(f'エラー内容: {response.get_data(as_text=True)}')
        else:
            print('テスト成功!')
            
except Exception as e:
    print(f'テストエラー: {e}')
    import traceback
    traceback.print_exc()

print('=== テスト完了 ===')