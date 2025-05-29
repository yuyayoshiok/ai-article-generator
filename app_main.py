from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
from anthropic import Anthropic
import google.generativeai as genai
import logging
import time
from functools import wraps
from urllib.parse import quote
from bs4 import BeautifulSoup
import random

# 環境変数の読み込み
load_dotenv()

app = Flask(__name__, static_folder='client/build/static', static_url_path='/static')
CORS(app, origins=[
    'http://localhost:3000', 
    'http://localhost:5001',
    'https://ai-article-generator-rfro.onrender.com'
])

# ログ設定
logging.basicConfig(level=logging.INFO)

# Unsplash APIの設定（環境変数から取得）
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')
UNSPLASH_SECRET_KEY = os.getenv('UNSPLASH_SECRET_KEY')

# AI クライアントの初期化
anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# ゆうや文体再現プロンプト
WRITING_STYLE_PROMPT = """
あなたは「ゆうや」という人物の文体を完全に再現して記事を書いてください。以下の特徴を厳密に守ってください：

【基本設定】
- 一人称：「僕」を使用
- 読者呼びかけ：「皆さん」
- 文体：です・ます調（丁寧語ベース）
- 文長：1文20-30文字程度の短文中心

【語彙・表現の特徴】
1. プロフェッショナルな表現を中心に、親しみやすさを保つ
   - 基本的には丁寧語・敬語ベース
   - 「実際のところ」「確実に」「明らかに」「具体的には」
   - 「〜については」「〜に関して」「〜という観点から」

2. 強調表現を適度に使用
   - 「めっちゃ」「圧倒的に」「かなり」「結構」
   - 「マスト」などのカタカナ語も常識範囲で使用

3. データに基づいた説得力のある表現
   - 「統計によると」「研究結果によれば」「専門家の見解では」
   - 「データが示すように」「事実として」「実証されている」

4. 読者に寄り添いつつ権威性のある表現
   - 「！」「？」は控えめに使用（重要な部分のみ）
   - 「…」での余韻表現も適度に抑制
   - 断定的すぎず、根拠を示した上での主張

【文章構造】
1. 改行とリズム（重要：頻繁な改行で読みやすく）
   - 1-2文ごとに改行を入れる
   - 段落は短く、3-4文程度で区切る
   - 長い文は途中で改行して読みやすく
   - 見出し後は必ず改行を入れる

2. 括弧の多用
   - 補足説明：「（〜のこと）」
   - 感情表現：「（涙）」「（汗）」
   - 疑問・強調：「（？）」「（！）」

3. 箇条書きの活用
   - 「・」「-」を使ったリスト
   - 見出し構造（# ## ###）を適切に使用

【内容・トーン】
1. 体験談ベース
   - 「僕は〜しています」「〜してみました」
   - 具体的な数字や実例を含める
   - 失敗談や恥ずかしい体験も率直に

2. 感情表現
   - 「嬉しい」「楽しい」「辛い」など率直な感情
   - 内心の葛藤や迷い「〜だと思います」「〜かもしれません」

3. 読者との距離感
   - 親しみやすいが礼儀正しい
   - 押し付けがましくない提案「〜かもです」

【記事構成】
1. 導入部
   - 「皆さんこんにちは。ゆうやと申します。」
   - 「本日の記事では「〜」について書いていきます。」

2. 本文
   - 体験談を交えた具体的な内容
   - メリット・デメリットなど整理された構成
   - 適度な脱線や余談も含める

3. 締めくくり
   - 「皆さん、お疲れ様でした。」
   - 「この記事では「〜」について書いてきました。」
   - 「参考になれば幸いです！」
   - 「ありがとうございました！」

【専門用語・説明】
- 専門用語は使用後に「（〜のこと）」で補足
- 「要するに」「簡単に言うと」「ざっくり言うと」で分かりやすく
- データは抽象的表現（「結構」「かなり」など）

【避けるべき表現】
- 「〜ですよね？」「〜じゃないですか？」（同意強要）
- 「で、」「あと、」（カジュアルすぎる接続詞）
- 「〜ですが、〜なんですよね」（複雑な複文）
- 執筆過程への言及（「書いている私も」など）

【記号使用ルール】
- 感嘆符：「！」「！！」（重ねても可）
- 三点リーダー：「…」（迷いや余韻）
- 括弧：（）で補足、【】""で強調
- 太字：**重要部分**で使用

【出雲弁（方言）の使用】
- 常識の範囲内で自然に混ぜる
- 「〜だけん」など（使いすぎない）

記事はMarkdown形式で出力し、この文体で読者に寄り添いながらも個性的で親しみやすい記事を作成してください。
"""

def rate_limit(max_requests=60, window=3600):
    """
    APIリクエストのレート制限デコレータ
    1時間あたり最大60リクエストに制限
    """
    def decorator(f):
        requests_log = []
        
        @wraps(f)
        def wrapper(*args, **kwargs):
            now = time.time()
            # 古いリクエストログを削除
            requests_log[:] = [req_time for req_time in requests_log if now - req_time < window]
            
            if len(requests_log) >= max_requests:
                app.logger.warning("レート制限に達しました")
                return jsonify({'error': 'リクエスト数制限に達しました'}), 429
            
            requests_log.append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator

def duckduckgo_news_search(query: str, limit: int = 5) -> str:
    """
    DuckDuckGoでニュースを検索（複数の検索戦略を試行）
    改良版の検索アルゴリズムを使用
    """
    # 検索件数の設定（最大10件）
    limit = min(limit, 10)
    
    # 人名や日本語キーワードに特化した検索戦略
    search_queries = [
        f"{query} ニュース",
        f"{query} 最新",
        f"{query} 話題",
        f"{query} 2024",
        f"{query} 情報",
        query  # オリジナルクエリも試行
    ]
    
    for i, search_query in enumerate(search_queries):
        try:
            # レート制限対策
            if i > 0:
                time.sleep(random.uniform(1, 3))
            
            encoded_query = quote(search_query)
            
            # より多様なUser-Agentとヘッダー
            user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
            ]
            
            headers = {
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            # 異なるDuckDuckGoエンドポイントを試行
            urls = [
                f"https://duckduckgo.com/?q={encoded_query}&iar=news&ia=news",
                f"https://html.duckduckgo.com/html/?q={encoded_query}&iar=news&ia=news",
                f"https://duckduckgo.com/html/?q={encoded_query}&t=h_&iar=news&ia=news"
            ]
            
            for url in urls:
                try:
                    response = requests.get(url, headers=headers, timeout=20)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        results = []
                        # 複数のセレクターパターンを試行
                        selectors = [".result__body", ".result", ".web-result", ".results_links"]
                        
                        for selector in selectors:
                            if len(results) >= limit:
                                break
                            for result in soup.select(selector):
                                if len(results) >= limit:
                                    break
                                title_elem = result.select_one(".result__title, .result__a, .result-title, a[href*='udm.gg']")
                                snippet_elem = result.select_one(".result__snippet, .result__desc, .result-snippet")
                                
                                if title_elem:
                                    title = title_elem.get_text(strip=True)
                                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                                    if title and len(title) > 10 and f"{title}: {snippet}" not in results:
                                        results.append(f"{title}: {snippet}")
                        
                        if results:
                            app.logger.info(f"DuckDuckGoニュース検索成功 (クエリ: '{search_query}', 結果: {len(results)}件)")
                            return "\n".join(results)
                
                except requests.exceptions.RequestException:
                    continue
                
        except Exception as e:
            app.logger.warning(f"DuckDuckGoニュース検索エラー (クエリ: '{search_query}'): {e}")
            continue
    
    # すべての検索戦略が失敗した場合
    app.logger.warning("すべてのDuckDuckGoニュース検索戦略が失敗しました")
    return ""


@app.route('/api/search', methods=['POST'])
@rate_limit()
def search_facts():
    """
    DuckDuckGoを使用したファクトチェック機能
    改良された検索アルゴリズムを使用してより正確な情報を取得
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        limit = data.get('limit', 5)
        
        app.logger.info(f"ファクトチェック検索開始: {query}")
        
        # 改良されたDuckDuckGo検索を実行
        search_results = duckduckgo_news_search(query, limit)
        
        if search_results:
            # 結果を構造化
            results_list = search_results.split('\n')
            structured_results = []
            
            for result in results_list:
                if ':' in result:
                    title, snippet = result.split(':', 1)
                    structured_results.append({
                        'title': title.strip(),
                        'snippet': snippet.strip()
                    })
            
            app.logger.info(f"検索結果取得完了: {len(structured_results)}件")
            
            return jsonify({
                'results': structured_results,
                'raw_results': search_results,
                'query_used': query,
                'success': True
            })
        else:
            # フォールバック: 従来のAPIも試行
            try:
                url = "https://api.duckduckgo.com/"
                params = {
                    'q': query,
                    'format': 'json',
                    'no_html': '1',
                    'skip_disambig': '1'
                }
                
                response = requests.get(url, params=params, timeout=10)
                search_data = response.json()
                
                fallback_results = []
                for topic in search_data.get('RelatedTopics', [])[:limit]:
                    if isinstance(topic, dict) and 'Text' in topic:
                        fallback_results.append({
                            'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                            'snippet': topic['Text']
                        })
                
                if fallback_results:
                    app.logger.info(f"フォールバック検索成功: {len(fallback_results)}件")
                    return jsonify({
                        'results': fallback_results,
                        'query_used': query,
                        'success': True,
                        'fallback': True
                    })
            
            except Exception as fallback_error:
                app.logger.error(f"フォールバック検索もエラー: {fallback_error}")
            
            return jsonify({
                'results': [],
                'query_used': query,
                'success': False,
                'message': '検索結果が見つかりませんでした'
            })
    
    except Exception as e:
        app.logger.error(f"検索エラー: {e}")
        return jsonify({'error': '検索に失敗しました'}), 500

@app.route('/api/images', methods=['POST'])
@rate_limit()
def get_images():
    """
    Unsplash APIを使用して無料素材画像を取得
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        app.logger.info(f"画像検索開始: {query}")
        
        # Unsplash APIのエンドポイント
        url = "https://api.unsplash.com/search/photos"
        headers = {
            'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'
        }
        params = {
            'query': query,
            'per_page': 5,
            'orientation': 'landscape'
        }
        
        response = requests.get(url, headers=headers, params=params)
        search_data = response.json()
        
        images = []
        for photo in search_data.get('results', []):
            images.append({
                'url': photo['urls']['regular'],
                'thumb': photo['urls']['thumb'],
                'alt': photo.get('alt_description') or query,
                'credit': f"Photo by {photo['user']['name']} on Unsplash"
            })
        
        app.logger.info(f"画像取得完了: {len(images)}枚")
        
        return jsonify({'images': images})
    
    except Exception as e:
        app.logger.error(f"画像検索エラー: {e}")
        return jsonify({'error': '画像検索に失敗しました'}), 500

def generate_buzz_title(keyword: str, content_preview: str = "") -> str:
    """
    Geminiを使ってバズるタイトルを生成
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        以下のキーワードと内容に基づいて、noteでバズりやすい魅力的なタイトルを生成してください。

        キーワード: {keyword}
        記事内容のプレビュー: {content_preview[:300]}...

        タイトル生成の要件：
        1. 【】で始まるカテゴリ表記を含める（例：【プログラミング】【AI】【体験談】等）
        2. 読者の興味を引く感情的なフック
        3. 具体性と数字を含める
        4. 40文字以内
        5. バズりやすいパターンを使用：
           - 「〜してみた結果」「〜が変わった話」
           - 「〜で人生が変わった」「〜のリアル」
           - 「知らないと損する〜」「〜の真実」
           - 「〜歳の私が〜」「〜日で〜」

        魅力的なタイトルを3つ提案し、最も良いものを1つ選んで返してください。
        形式: タイトルのみを返す（説明不要）
        """
        
        response = model.generate_content(prompt)
        title = response.text.strip()
        
        # 複数のタイトルが返された場合、最初のものを使用
        if '\n' in title:
            title = title.split('\n')[0].strip()
        
        app.logger.info(f"生成されたバズタイトル: {title}")
        return title
        
    except Exception as e:
        app.logger.error(f"タイトル生成エラー: {e}")
        return f"【{keyword}】{keyword}について詳しく解説してみた"

@app.route('/api/generate', methods=['POST'])
@rate_limit()
def generate_article():
    try:
        data = request.get_json()
        keyword = data.get('keyword', '')
        ai_model = data.get('model', 'claude')
        include_images = data.get('includeImages', True)
        generate_title = data.get('generateTitle', True)
        
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        # ファクトチェック機能の実行
        fact_check_results = None
        if data.get('factCheck', True):
            try:
                fact_check_results = duckduckgo_news_search(keyword, 3)
                if fact_check_results:
                    app.logger.info(f"ファクトチェック情報取得成功: {len(fact_check_results)}文字")
                else:
                    app.logger.warning("ファクトチェック情報の取得に失敗")
            except Exception as fact_error:
                app.logger.error(f"ファクトチェックエラー: {fact_error}")
                fact_check_results = None
        
        # より詳細な研究・ファクトチェック情報の取得
        research_data = ""
        if fact_check_results:
            research_data = f"最新情報・ニュース:\n{fact_check_results}\n\n"
        
        # 追加の検索クエリで詳細情報を取得
        additional_searches = [
            f"{keyword} 統計 データ",
            f"{keyword} 専門家 意見",
            f"{keyword} メリット デメリット",
            f"{keyword} 事例 実例"
        ]
        
        for search_query in additional_searches:
            try:
                additional_results = duckduckgo_news_search(search_query, 2)
                if additional_results:
                    research_data += f"{search_query}に関する情報:\n{additional_results}\n\n"
            except Exception as e:
                app.logger.warning(f"追加検索エラー ({search_query}): {e}")
        
        prompt = f"""
        {WRITING_STYLE_PROMPT}
        
        キーワード: {keyword}
        
        このキーワードについて、以下の研究データを参考に、詳細で信頼性の高い記事を作成してください。
        
        【研究・ファクトチェックデータ】:
        {research_data if research_data else 'データなし - 一般的な知識に基づいて作成'}
        
        記事作成の要件：
        
        【プロフェッショナルな文章構成】
        以下の「起承転結」構成で、論理的かつ説得力のある記事を作成してください：
        
        1. 【起】問題提起・フック（全体の20%）
           - 読者の注目を引く印象的な導入
           - 問題意識の明確化（「〜で困っていませんか？」「〜という課題があります」）
           - 統計データや衝撃的な事実の提示
           - 記事を読む価値（ベネフィット）の明示
        
        2. 【承】現状分析・背景説明（全体の30%）
           - 問題の詳細な分析と原因究明
           - 専門家の見解や研究データの引用
           - 関連する事例や統計の提示
           - なぜこの問題が重要なのかの説明
        
        3. 【転】解決策・新たな視点（全体の35%）
           - 具体的な解決方法の提示（最低3つ）
           - 各解決策のメリット・デメリット
           - 実践的なステップバイステップガイド
           - 成功事例や体験談の紹介
        
        4. 【結】まとめ・行動喚起（全体の15%）
           - 重要ポイントの再確認
           - 読者への具体的なアクションプラン
           - 未来への展望やビジョン
           - 力強いクロージングメッセージ
        
        【文章テクニック】
        - 各章に明確な見出しを設定
        - 重要な情報は箇条書きで整理
        - データは具体的な数字で示す（「多い」→「72%」）
        - 専門用語には必ず説明を付ける
        - 1段落3-4文、1文20-30文字を基本に
        - 接続詞を効果的に使用（「しかし」「さらに」「つまり」）
        - 読者への問いかけを適度に挿入
        
        【プロフェッショナルな要素】
        - 権威性：専門家の引用、公的機関のデータ
        - 信頼性：出典の明記、客観的な分析
        - 実用性：すぐに実践できるアドバイス
        - 独自性：他にない視点や体験談
        """
        
        if ai_model == 'claude':
            try:
                response = anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=5000,
                    messages=[{"role": "user", "content": prompt}]
                )
                article_content = response.content[0].text
            except Exception as claude_error:
                app.logger.error(f"Claude API エラー: {claude_error}")
                return jsonify({'error': f'Claude API エラー: {str(claude_error)}'}), 500
        else:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                article_content = response.text
            except Exception as gemini_error:
                app.logger.error(f"Gemini API エラー: {gemini_error}")
                return jsonify({'error': f'Gemini API エラー: {str(gemini_error)}'}), 500
        
        result = {'content': article_content}
        
        # バズるタイトルを生成
        if generate_title:
            try:
                buzz_title = generate_buzz_title(keyword, article_content)
                result['suggested_title'] = buzz_title
                app.logger.info(f"バズタイトル生成完了: {buzz_title}")
            except Exception as title_error:
                app.logger.error(f"タイトル生成エラー: {title_error}")
                result['suggested_title'] = f"【{keyword}】{keyword}について詳しく解説してみた"
        
        if include_images:
            try:
                # 記事に適した画像を取得
                image_keywords = [
                    keyword,
                    f"{keyword} 関連",
                    f"{keyword} イメージ"
                ]
                
                images = []
                for img_keyword in image_keywords:
                    try:
                        image_response = requests.post('http://localhost:5001/api/images',
                                                     json={'query': img_keyword})
                        if image_response.status_code == 200:
                            keyword_images = image_response.json().get('images', [])
                            images.extend(keyword_images[:2])  # 各キーワードから2枚まで
                            if len(images) >= 6:  # 最大6枚まで
                                break
                    except Exception as img_error:
                        app.logger.warning(f"画像取得エラー ({img_keyword}): {img_error}")
                        continue
                
                if images:
                    result['images'] = images[:6]  # 最終的に6枚まで
                    app.logger.info(f"関連画像取得完了: {len(result['images'])}枚")
                else:
                    app.logger.warning("関連画像の取得に失敗")
                    
            except Exception as img_error:
                app.logger.warning(f"画像取得エラー: {img_error}")
                # 画像取得失敗は致命的ではないので続行
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Generation error: {e}")
        return jsonify({'error': 'Article generation failed'}), 500

@app.route('/api/rewrite', methods=['POST'])
@rate_limit()
def rewrite_article():
    try:
        data = request.get_json()
        original_text = data.get('text', '')
        ai_model = data.get('model', 'claude')
        rewrite_type = data.get('type', 'improve')
        
        if not original_text:
            return jsonify({'error': 'Text is required'}), 400
        
        rewrite_prompts = {
            'improve': f'''{WRITING_STYLE_PROMPT}

以下の文章を、プロフェッショナルな「起承転結」構成で書き直してください：

【元の文章】
{original_text}

【リライト要件】
1. 【起】（20%）- 強力な問題提起から始める
   - 読者の注目を引くフック
   - 明確な問題意識の提示
   - 記事の価値を示す

2. 【承】（30%）- 詳細な現状分析
   - 背景情報の整理
   - データや統計の活用
   - 論理的な説明の展開

3. 【転】（35%）- 解決策の提示
   - 具体的な方法論
   - 実践可能なステップ
   - 成功事例の紹介

4. 【結】（15%）- 力強いまとめ
   - 要点の再確認
   - 行動への呼びかけ
   - 印象的なクロージング

必ず「ゆうや」の文体を維持しながら、プロフェッショナルな構成に改善してください。'''
        }
        
        prompt = rewrite_prompts.get(rewrite_type, rewrite_prompts['improve'])
        
        if ai_model == 'claude':
            try:
                response = anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=3000,
                    messages=[{"role": "user", "content": prompt}]
                )
                rewritten_content = response.content[0].text
            except Exception as claude_error:
                app.logger.error(f"Claude API エラー: {claude_error}")
                return jsonify({'error': f'Claude API エラー: {str(claude_error)}'}), 500
        else:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                rewritten_content = response.text
            except Exception as gemini_error:
                app.logger.error(f"Gemini API エラー: {gemini_error}")
                return jsonify({'error': f'Gemini API エラー: {str(gemini_error)}'}), 500
        
        return jsonify({'content': rewritten_content})
    
    except Exception as e:
        app.logger.error(f"Rewrite error: {e}")
        return jsonify({'error': 'Article rewrite failed'}), 500

@app.route('/api/publish', methods=['POST'])
@rate_limit()
def publish_article():
    """
    記事を各プラットフォームに投稿（進捗状況付き）
    """
    try:
        data = request.get_json()
        platform = data.get('platform', '')
        title = data.get('title', '')
        content = data.get('content', '')
        
        if not all([platform, title, content]):
            return jsonify({'error': '必要な情報が不足しています'}), 400
        
        app.logger.info(f"記事投稿開始: {platform}")
        
        # 進捗状況を記録（シンプルな実装）
        app.logger.info(f"投稿プロセス開始: {platform}")
        
        if platform == 'note':
            result = publish_to_note(title, content)
        elif platform == 'qiita':
            result = publish_to_qiita(title, content)
        elif platform == 'zenn':
            result = publish_to_zenn(title, content)
        else:
            return jsonify({'error': 'サポートされていないプラットフォームです'}), 400
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"投稿エラー: {e}")
        return jsonify({'error': '投稿に失敗しました'}), 500

def publish_to_note(title: str, content: str):
    """
    noteに記事を投稿（手動投稿モード）
    """
    try:
        app.logger.info("note手動投稿モードで実行")
        
        return {
            'success': True,
            'platform': 'note',
            'message': '記事の準備が完了しました！',
            'url': 'https://note.com/post',
            'instructions': '1. 「noteで投稿する」をクリック\n2. ログイン後、下記のタイトルと本文をコピー＆ペースト\n3. 公開設定を選択して投稿してください',
            'manual_mode': True,
            'title': title,
            'content': content
        }
    
    except Exception as e:
        app.logger.error(f"note投稿エラー: {e}")
        return {
            'success': False,
            'platform': 'note',
            'error': str(e),
            'message': '手動投稿を推奨：生成されたMarkdownをコピーしてnoteエディタに貼り付けてください',
            'url': 'https://note.com/post',
            'manual_mode': True,
            'title': title,
            'content': content
        }

def publish_to_qiita(title: str, content: str):
    """
    Qiitaに記事を投稿
    """
    try:
        qiita_token = os.getenv('QIITA_ACCESS_TOKEN')
        if not qiita_token:
            return {
                'success': False,
                'error': 'Qiitaのアクセストークンが設定されていません'
            }
        
        url = 'https://qiita.com/api/v2/items'
        headers = {
            'Authorization': f'Bearer {qiita_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'title': title,
            'body': content,
            'private': True,  # デフォルトは下書き
            'tags': [
                {'name': 'AI', 'versions': ['']},
                {'name': '記事生成', 'versions': ['']}
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            result = response.json()
            return {
                'success': True,
                'platform': 'qiita',
                'url': result['url'],
                'id': result['id'],
                'message': '下書きとして投稿されました'
            }
        else:
            return {
                'success': False,
                'error': f'Qiita API エラー: {response.status_code}'
            }
    
    except Exception as e:
        app.logger.error(f"Qiita投稿エラー: {e}")
        return {'success': False, 'error': str(e)}

def publish_to_zenn(title: str, content: str):
    """
    Zennに記事を投稿（GitHub連携）
    """
    try:
        # ZennはGitHub連携での投稿が主流
        return {
            'success': True,
            'platform': 'zenn',
            'message': 'Zennへの投稿はGitHub経由で行ってください',
            'instructions': 'ZennとGitHubを連携し、articles/フォルダにMarkdownファイルを配置してください',
            'filename_suggestion': f"{str(title).replace(' ', '-').lower()}.md"
        }
    except Exception as e:
        app.logger.error(f"Zenn投稿エラー: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    build_dir = os.path.join(os.path.dirname(__file__), 'client', 'build')
    full_path = os.path.join(build_dir, path) if path else build_dir
    
    app.logger.info(f"Requesting path: {path}")
    app.logger.info(f"Build directory: {build_dir}")
    app.logger.info(f"Full path: {full_path}")
    app.logger.info(f"Path exists: {os.path.exists(full_path)}")
    
    if path and os.path.exists(full_path):
        app.logger.info(f"Serving file: {path}")
        return send_from_directory(build_dir, path)
    
    app.logger.info("Serving index.html")
    return send_from_directory(build_dir, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_ENV', 'production') == 'development'
    
    print(f"サーバーをポート{port}で起動中...")
    print(f"デバッグモード: {debug_mode}")
    
    if debug_mode:
        # 開発環境でのポートチェック
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('localhost', port))
            if result == 0:
                print(f"警告: ポート{port}は既に使用中です")
                for test_port in range(5001, 5010):
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_s:
                        if test_s.connect_ex(('localhost', test_port)) != 0:
                            port = test_port
                            break
        print(f"アクセスURL: http://localhost:{port}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug_mode, threaded=True)
    except OSError as e:
        print(f"サーバー起動エラー: {e}")
        if debug_mode:
            print("別のプロセスがポートを使用している可能性があります。")
    except KeyboardInterrupt:
        print("\nサーバーを停止しました。")