const express = require('express');
const router = express.Router();
const { Anthropic } = require('@anthropic-ai/sdk');
const { GoogleGenerativeAI } = require('@google/generative-ai');

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_AI_API_KEY);

const getUserStylePrompt = () => {
  return `あなたは経験豊富なライターです。以下の文体と特徴を模倣してリライトしてください：

文体の特徴：
- 読者との距離感を大切にし、親しみやすい口調
- 専門的な内容も分かりやすく説明
- 具体例や体験談を交える
- 実用的で行動に移しやすい内容
- 適度にユーモアを交える
- 結論を明確に示す

リライトの方針：
- 元の内容の意味を保ちながら、より読みやすく改善
- SEOを意識した構成に調整
- 見出し構造を最適化
- 読者にとってより価値のある内容に発展

必ずMarkdown形式で出力してください。`;
};

router.post('/', async (req, res) => {
  try {
    const { originalText, aiProvider, stylePrompt, rewriteType = 'improve' } = req.body;

    if (!originalText) {
      return res.status(400).json({ error: '元の文章が必要です' });
    }

    const basePrompt = stylePrompt || getUserStylePrompt();
    
    let specificInstructions = '';
    switch (rewriteType) {
      case 'improve':
        specificInstructions = '内容をより良く、読みやすく改善してください。';
        break;
      case 'shorten':
        specificInstructions = '要点を保ちながら、より簡潔にまとめてください。';
        break;
      case 'expand':
        specificInstructions = '内容をより詳しく、具体例を交えて拡充してください。';
        break;
      case 'tone':
        specificInstructions = '文体とトーンを統一し、より親しみやすい表現に変更してください。';
        break;
      default:
        specificInstructions = '内容をより良く、読みやすく改善してください。';
    }

    const prompt = `${basePrompt}

リライト指示: ${specificInstructions}

元の文章:
${originalText}

上記の文章を指示に従ってリライトしてください。
必ずMarkdown形式で出力し、適切な見出し構造を使用してください。`;

    let rewrittenText;

    if (aiProvider === 'claude') {
      const response = await anthropic.messages.create({
        model: 'claude-3-sonnet-20240229',
        max_tokens: 4000,
        messages: [{ role: 'user', content: prompt }]
      });
      rewrittenText = response.content[0].text;
    } else {
      const model = genAI.getGenerativeModel({ model: 'gemini-pro' });
      const result = await model.generateContent(prompt);
      const response = await result.response;
      rewrittenText = response.text();
    }

    res.json({
      originalText,
      rewrittenText,
      aiProvider,
      rewriteType
    });

  } catch (error) {
    console.error('リライトエラー:', error);
    res.status(500).json({ error: 'リライト中にエラーが発生しました' });
  }
});

module.exports = router;