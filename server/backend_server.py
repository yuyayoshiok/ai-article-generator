#!/usr/bin/env python3
"""
バックエンドサーバー - ポート3001で起動
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import threading
import time

app = Flask(__name__)
CORS(app, origins=['*'])  # 開発時は全て許可

@app.route('/api/test')
def test():
    return jsonify({'message': 'Backend server is running!', 'port': 3001})

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        keyword = data.get('keyword', 'テスト')
        
        # モック記事生成
        content = f"""# {keyword}について

皆さんこんにちは。ゆうやと申します。
本日の記事では「{keyword}」について書いていきます。

## {keyword}の特徴

{keyword}はめっちゃ興味深いトピックですね！
僕も調べてみたのですが、かなり奥が深いです。

実際に使ってみた感想としては：
- 使いやすい
- 機能が豊富
- 学習コストはちょっと高いかも

## まとめ

皆さん、お疲れ様でした。
この記事では「{keyword}」について書いてきました。
参考になれば幸いです！

ありがとうございました！"""

        return jsonify({'content': content})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rewrite', methods=['POST'])
def rewrite():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        content = f"""# リライト結果

{text}

（ゆうやの文体でリライトされました！）"""

        return jsonify({'content': content})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_server():
    app.run(host='127.0.0.1', port=3001, debug=False, threaded=True)

if __name__ == '__main__':
    print("🚀 バックエンドサーバー起動中...")
    print("📡 ポート: 3001")
    print("🌐 URL: http://localhost:3001")
    print("✅ テスト: http://localhost:3001/api/test")
    print("-" * 50)
    
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n🛑 サーバーを停止しました")
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)