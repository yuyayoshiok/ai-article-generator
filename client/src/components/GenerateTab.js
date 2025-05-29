import React, { useState } from 'react';
import { Sparkles, Search, Image } from 'lucide-react';
import axios from 'axios';
import ResultModal from './ResultModal';
import { API_BASE_URL } from '../config';

function GenerateTab() {
  // 状態管理
  const [keyword, setKeyword] = useState('');
  const [selectedModel, setSelectedModel] = useState('gemini');
  const [includeImages, setIncludeImages] = useState(true);
  const [factCheck, setFactCheck] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);

  // 記事生成処理
  const handleGenerate = async () => {
    if (!keyword.trim()) {
      setError('キーワードを入力してください');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      console.log('記事生成開始:', { keyword, selectedModel, includeImages, factCheck });
      
      const response = await axios.post(`${API_BASE_URL}/api/generate`, {
        keyword: keyword.trim(),
        model: selectedModel,
        includeImages,
        factCheck
      });

      console.log('記事生成完了:', response.data);
      setResult(response.data);
      setModalOpen(true); // 生成完了後にモーダルを開く
    } catch (err) {
      console.error('記事生成エラー:', err);
      setError(err.response?.data?.error || '記事生成に失敗しました');
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="generate-tab">
      {/* 入力フォームセクション */}
      <div className="form-section">
        <h2 className="section-title">
          <Sparkles size={24} />
          記事生成設定
        </h2>
        
        {/* キーワード入力 */}
        <div className="form-group">
          <label className="form-label">キーワード</label>
          <input
            type="text"
            className="form-input"
            placeholder="記事のテーマとなるキーワードを入力..."
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            disabled={loading}
          />
        </div>

        {/* AIモデル選択 */}
        <div className="form-group">
          <label className="form-label">AIモデル</label>
          <div className="model-selector">
            <div
              className={`model-option ${selectedModel === 'claude' ? 'selected' : ''}`}
              onClick={() => !loading && setSelectedModel('claude')}
            >
              Claude
            </div>
            <div
              className={`model-option ${selectedModel === 'gemini' ? 'selected' : ''}`}
              onClick={() => !loading && setSelectedModel('gemini')}
            >
              Gemini
            </div>
          </div>
        </div>

        {/* オプション設定 */}
        <div className="form-group">
          <div className="checkbox-group">
            <input
              type="checkbox"
              id="factCheck"
              className="checkbox"
              checked={factCheck}
              onChange={(e) => setFactCheck(e.target.checked)}
              disabled={loading}
            />
            <label htmlFor="factCheck" className="checkbox-label">
              <Search size={16} />
              ファクトチェック機能を使用
            </label>
          </div>
          
          <div className="checkbox-group">
            <input
              type="checkbox"
              id="includeImages"
              className="checkbox"
              checked={includeImages}
              onChange={(e) => setIncludeImages(e.target.checked)}
              disabled={loading}
            />
            <label htmlFor="includeImages" className="checkbox-label">
              <Image size={16} />
              関連画像を自動挿入
            </label>
          </div>
        </div>

        {/* 生成ボタン */}
        <button
          className="generate-button"
          onClick={handleGenerate}
          disabled={loading || !keyword.trim()}
        >
          {loading ? (
            <>
              <div className="loading-spinner"></div>
              記事生成中...
            </>
          ) : (
            <>
              <Sparkles size={20} />
              記事を生成
            </>
          )}
        </button>

        {/* エラーメッセージ */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
      </div>

      {/* 結果モーダル */}
      <ResultModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        result={result}
        title="生成された記事"
      />
    </div>
  );
}

export default GenerateTab;