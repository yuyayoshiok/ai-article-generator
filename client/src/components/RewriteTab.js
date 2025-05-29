import React, { useState } from 'react';
import { Edit3, Wand2 } from 'lucide-react';
import axios from 'axios';
import ResultModal from './ResultModal';
import { API_BASE_URL } from '../config';

function RewriteTab() {
  // 状態管理
  const [originalText, setOriginalText] = useState('');
  const [selectedModel, setSelectedModel] = useState('claude');
  const [rewriteType, setRewriteType] = useState('improve');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);

  // リライトタイプの定義
  const rewriteTypes = [
    { id: 'improve', label: '品質向上', description: 'より読みやすく魅力的に' }
  ];

  // リライト処理
  const handleRewrite = async () => {
    if (!originalText.trim()) {
      setError('リライトする文章を入力してください');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      console.log('リライト開始:', { 
        textLength: originalText.length, 
        selectedModel, 
        rewriteType 
      });
      
      const response = await axios.post(`${API_BASE_URL}/api/rewrite`, {
        text: originalText.trim(),
        model: selectedModel,
        type: rewriteType
      });

      console.log('リライト完了:', response.data);
      setResult(response.data);
      setModalOpen(true); // リライト完了後にモーダルを開く
    } catch (err) {
      console.error('リライトエラー:', err);
      setError(err.response?.data?.error || 'リライトに失敗しました');
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="rewrite-tab">
      {/* 入力フォームセクション */}
      <div className="form-section">
        <h2 className="section-title">
          <Edit3 size={24} />
          リライト設定
        </h2>
        
        {/* 元テキスト入力 */}
        <div className="form-group">
          <label className="form-label">リライトする文章</label>
          <textarea
            className="form-input form-textarea"
            placeholder="リライトしたい文章を入力してください..."
            value={originalText}
            onChange={(e) => setOriginalText(e.target.value)}
            disabled={loading}
            rows={12}
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


        {/* リライトボタン */}
        <button
          className="generate-button"
          onClick={handleRewrite}
          disabled={loading || !originalText.trim()}
        >
          {loading ? (
            <>
              <div className="loading-spinner"></div>
              リライト中...
            </>
          ) : (
            <>
              <Wand2 size={20} />
              リライト実行
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
        title="リライト結果"
      />
    </div>
  );
}

export default RewriteTab;