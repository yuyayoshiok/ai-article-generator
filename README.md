# AI記事生成ツール

Claude & Gemini AI を活用した高品質な記事生成ツールです。ファクトチェック機能、画像挿入、複数プラットフォーム投稿に対応しています。

## 機能

- 🤖 **AI記事生成**: Claude 3.5 Sonnet と Gemini 1.5 Flash による高品質な記事作成
- 🔍 **ファクトチェック**: DuckDuckGo検索による最新情報の取得と統計データの確認
- 🖼️ **画像挿入**: Unsplash APIによる関連画像の自動取得
- 📝 **文体再現**: 「ゆうや」独自の親しみやすい文体を完全再現
- 📱 **レスポンシブデザイン**: スマートフォンでも快適に利用可能
- 🚀 **プラットフォーム対応**: note、Qiita、Zennへの投稿サポート

## 技術スタック

### フロントエンド
- React 18
- CSS3 (Flexbox/Grid)
- Responsive Design

### バックエンド
- Python 3.11
- Flask
- Flask-CORS

### AI & API
- Anthropic Claude API
- Google Gemini API
- Unsplash API
- DuckDuckGo Search

## 環境変数

以下の環境変数を設定してください：

```env
# AI API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key
GEMINI_API_KEY=your_gemini_api_key

# Image API
UNSPLASH_ACCESS_KEY=your_unsplash_access_key
UNSPLASH_SECRET_KEY=your_unsplash_secret_key

# Platform API (オプション)
QIITA_ACCESS_TOKEN=your_qiita_token
```

## ローカル開発

### 必要条件
- Python 3.11+
- Node.js 16+

### セットアップ

1. リポジトリをクローン
```bash
git clone https://github.com/yourusername/ai-article-generator.git
cd ai-article-generator
```

2. バックエンドのセットアップ
```bash
cd server
pip install -r requirements.txt
```

3. フロントエンドのセットアップ
```bash
cd client
npm install
npm run build
```

4. 環境変数を設定
```bash
cp .env.example .env
# .env ファイルを編集してAPIキーを設定
```

5. アプリケーションを起動
```bash
cd server
python app.py
```

ブラウザで http://localhost:5001 にアクセス

## Renderでのデプロイ

1. GitHubリポジトリをRenderに接続
2. 環境変数を設定：
   - `ANTHROPIC_API_KEY`
   - `GEMINI_API_KEY`
   - `UNSPLASH_ACCESS_KEY`
   - `UNSPLASH_SECRET_KEY`
   - `QIITA_ACCESS_TOKEN` (オプション)
3. ビルド＆デプロイコマンドは自動設定されます

## 使用方法

1. **キーワード入力**: 記事にしたいキーワードを入力
2. **AI選択**: Claude または Gemini を選択
3. **オプション設定**: 
   - ファクトチェック機能
   - 画像挿入機能
   - タイトル自動生成
4. **記事生成**: 「記事を生成」ボタンをクリック
5. **投稿**: 各プラットフォームに投稿またはコピー&ペースト

## ライセンス

MIT License

## 開発者

- **ゆうや** - AI記事生成ツールの開発・運営