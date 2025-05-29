#!/usr/bin/env python3
"""
Render用のFlaskサーバー起動スクリプト
"""
import os
import sys

# server ディレクトリに移動
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

# Flask アプリをインポート
from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting Flask server on port {port}")
    
    # 本番環境設定
    app.config['DEBUG'] = False
    app.config['ENV'] = 'production'
    
    # Flaskサーバーを起動
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)