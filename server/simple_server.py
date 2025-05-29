#!/usr/bin/env python3
"""
シンプルなテストサーバー
接続問題のデバッグ用
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://localhost:5001'])

@app.route('/api/test', methods=['GET', 'POST'])
def test_endpoint():
    return jsonify({
        'status': 'success',
        'message': 'サーバー接続成功！',
        'method': request.method,
        'data': request.get_json() if request.method == 'POST' else None
    })

@app.route('/api/generate', methods=['POST'])
def simple_generate():
    data = request.get_json()
    keyword = data.get('keyword', 'デフォルト')
    
    # シンプルなモックレスポンス
    return jsonify({
        'content': f"""# {keyword}について

皆さんこんにちは。ゆうやと申します。
本日の記事では「{keyword}」について書いていきます。

## {keyword}とは？

{keyword}は最近注目されているトピックですね！
僕も実際に調べてみたのですが、めっちゃ興味深いです。

## まとめ

皆さん、お疲れ様でした。
この記事では「{keyword}」について書いてきました。
参考になれば幸いです！

ありがとうございました！"""
    })

@app.route('/api/rewrite', methods=['POST'])
def simple_rewrite():
    data = request.get_json()
    text = data.get('text', '')
    
    return jsonify({
        'content': f"""# リライト結果

{text}

（ゆうやの文体でリライトされました）"""
    })

if __name__ == '__main__':
    port = 5001
    print(f"=== シンプルテストサーバー起動 ===")
    print(f"ポート: {port}")
    print(f"URL: http://localhost:{port}")
    print(f"テストエンドポイント: http://localhost:{port}/api/test")
    print("=" * 40)
    
    try:
        # IPv4のみで起動を試す
        app.run(host='127.0.0.1', port=port, debug=True)
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()