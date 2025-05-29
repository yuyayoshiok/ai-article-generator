#!/usr/bin/env python3
"""
Render用のFlaskサーバー起動スクリプト
"""
import os
import sys
import traceback

def main():
    try:
        print("=== Flask Startup Debug Info ===")
        print(f"Python version: {sys.version}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        print(f"Environment PORT: {os.environ.get('PORT', 'not set')}")
        
        # server ディレクトリに移動
        server_path = os.path.join(os.path.dirname(__file__), 'server')
        print(f"Server path: {server_path}")
        print(f"Server path exists: {os.path.exists(server_path)}")
        
        if server_path not in sys.path:
            sys.path.insert(0, server_path)
        
        print("=== Importing Flask app ===")
        # Flask アプリをインポート
        from app import app
        print("Flask app imported successfully")
        
        port = int(os.environ.get('PORT', 5001))
        print(f"Starting Flask server on port {port}")
        
        # 本番環境設定
        app.config['DEBUG'] = False
        app.config['ENV'] = 'production'
        
        print("=== Starting Flask server ===")
        # Flaskサーバーを起動
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
        
    except Exception as e:
        print(f"=== ERROR: Flask startup failed ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("=== Full traceback ===")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()