const express = require('express');
const router = express.Router();
const { Anthropic } = require('@anthropic-ai/sdk');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const axios = require('axios');

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_AI_API_KEY);

const searchDuckDuckGo = async (query) => {
  try {
    const response = await axios.get(`https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json&no_html=1&skip_disambig=1`);
    return response.data;
  } catch (error) {
    console.error('DuckDuckGo search error:', error);
    return null;
  }
};

const getUserStylePrompt = () => {
  return `あなたは経験豊富なライターです。以下の文体と特徴を模倣して記事を書いてください：

文体の特徴：
- 読者との距離感を大切にし、親しみやすい口調
- 専門的な内容も分かりやすく説明
- 具体例や体験談を交える
- 実用的で行動に移しやすい内容
- 適度にユーモアを交える
- 結論を明確に示す

記事の構成：
1. 導入（読者の興味を引く）
2. 問題提起
3. 解決策の提示（複数の選択肢）
4. 具体的な実装方法
5. まとめと次のアクション

必ずMarkdown形式で出力してください。`;
};

router.post('/', async (req, res) => {
  try {
    const { keyword, aiProvider, stylePrompt } = req.body;

    if (!keyword) {
      return res.status(400).json({ error: 'キーワードが必要です' });
    }

    let searchResults = null;
    try {
      searchResults = await searchDuckDuckGo(keyword);
    } catch (error) {
      console.log('ファクトチェック検索でエラーが発生しました:', error);
    }

    const basePrompt = stylePrompt || getUserStylePrompt();
    const prompt = `${basePrompt}

キーワード: ${keyword}

${searchResults ? `
参考情報（ファクトチェック用）:
${JSON.stringify(searchResults.AbstractText || searchResults.Answer || '関連情報が見つかりませんでした', null, 2)}
` : ''}

上記のキーワードについて、SEOを意識した高品質な記事を作成してください。
記事は2000-3000文字程度で、読者にとって有益で実用的な内容にしてください。
必ずMarkdown形式で出力し、適切な見出し構造を使用してください。`;

    let article;

    if (aiProvider === 'claude') {
      const response = await anthropic.messages.create({
        model: 'claude-3-sonnet-20240229',
        max_tokens: 4000,
        messages: [{ role: 'user', content: prompt }]
      });
      article = response.content[0].text;
    } else {
      const model = genAI.getGenerativeModel({ model: 'gemini-pro' });
      const result = await model.generateContent(prompt);
      const response = await result.response;
      article = response.text();
    }

    res.json({
      article,
      keyword,
      aiProvider,
      factCheckUsed: !!searchResults
    });

  } catch (error) {
    console.error('記事生成エラー:', error);
    res.status(500).json({ error: '記事生成中にエラーが発生しました' });
  }
});

module.exports = router;