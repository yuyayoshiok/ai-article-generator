import React, { useState, useEffect } from 'react';
import { X, Copy, CheckCircle, Download, Send } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function ResultModal({ isOpen, onClose, result, title = "生成結果" }) {
  const [copied, setCopied] = useState(false);
  const [publishModalOpen, setPublishModalOpen] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState('note');
  const [articleTitle, setArticleTitle] = useState('');
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishResult, setPublishResult] = useState(null);

  // 投稿先プラットフォームの定義
  const platforms = [
    { id: 'note', name: 'note', url: 'https://note.com/', description: '気軽に投稿' },
    { id: 'qiita', name: 'Qiita', url: 'https://qiita.com/', description: '技術記事向け' },
    { id: 'zenn', name: 'Zenn', url: 'https://zenn.dev/', description: 'エンジニア向け' }
  ];

  // モーダルが開かれたときにスクロールを無効化
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    // クリーンアップ
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  // ESCキーでモーダルを閉じる
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  // クリップボードコピー機能
  const handleCopy = async () => {
    if (!result?.content) return;
    
    try {
      await navigator.clipboard.writeText(result.content);
      setCopied(true);
      console.log('クリップボードにコピー完了');
      
      // 2秒後にコピー状態をリセット
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('コピーエラー:', err);
    }
  };

  // テキストファイルとしてダウンロード
  const handleDownload = () => {
    if (!result?.content) return;

    const blob = new Blob([result.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'article.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // モーダルが開いた時に推奨タイトルを設定
  useEffect(() => {
    if (isOpen && result?.suggested_title && !articleTitle) {
      setArticleTitle(result.suggested_title);
    }
  }, [isOpen, result?.suggested_title, articleTitle]);

  // 投稿処理
  const handlePublish = async () => {
    if (!articleTitle.trim() || !result?.content) return;

    setIsPublishing(true);
    setPublishResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/publish`, {
        platform: selectedPlatform,
        title: articleTitle.trim(),
        content: result.content
      });

      if (response.data) {
        setPublishResult(response.data);
        if (response.data.success) {
          // 成功時は3秒後にモーダルを閉じる
          setTimeout(() => {
            setPublishModalOpen(false);
            setPublishResult(null);
            setArticleTitle('');
          }, 3000);
        }
      }
    } catch (error) {
      console.error('投稿エラー:', error);
      setPublishResult({
        success: false,
        message: '投稿に失敗しました。ネットワーク接続を確認してください。'
      });
    } finally {
      setIsPublishing(false);
    }
  };

  if (!isOpen || !result) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        {/* ヘッダー */}
        <div className="modal-header">
          <h2 className="modal-title">{title}</h2>
          <div className="modal-actions">
            <button 
              className="action-button copy-button"
              onClick={handleCopy}
              title="クリップボードにコピー"
            >
              {copied ? (
                <>
                  <CheckCircle size={16} />
                  コピー済み
                </>
              ) : (
                <>
                  <Copy size={16} />
                  コピー
                </>
              )}
            </button>
            
            <button 
              className="action-button download-button"
              onClick={handleDownload}
              title="Markdownファイルとしてダウンロード"
            >
              <Download size={16} />
              ダウンロード
            </button>
            
            <button 
              className="action-button publish-button"
              onClick={() => setPublishModalOpen(true)}
              title="投稿する"
            >
              <Send size={16} />
              投稿
            </button>
            
            <button 
              className="action-button close-button"
              onClick={onClose}
              title="閉じる"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* コンテンツ */}
        <div className="modal-content">
          {/* プレビュー */}
          <div className="preview-section">
            <h3 className="section-subtitle">プレビュー</h3>
            <div className="markdown-preview">
              <ReactMarkdown 
                components={{
                  p: ({children}) => <p style={{marginBottom: '1.2rem', lineHeight: '1.8'}}>{children}</p>,
                  h1: ({children}) => <h1 style={{margin: '1.5rem 0 1rem 0', lineHeight: '1.4'}}>{children}</h1>,
                  h2: ({children}) => <h2 style={{margin: '1.5rem 0 1rem 0', lineHeight: '1.4'}}>{children}</h2>,
                  h3: ({children}) => <h3 style={{margin: '1.5rem 0 1rem 0', lineHeight: '1.4'}}>{children}</h3>,
                  li: ({children}) => <li style={{marginBottom: '0.7rem', lineHeight: '1.7'}}>{children}</li>,
                  ul: ({children}) => <ul style={{margin: '1rem 0', paddingLeft: '2rem', lineHeight: '1.7'}}>{children}</ul>,
                  ol: ({children}) => <ol style={{margin: '1rem 0', paddingLeft: '2rem', lineHeight: '1.7'}}>{children}</ol>
                }}
              >
                {result.content}
              </ReactMarkdown>
            </div>
          </div>

          {/* Raw Markdown */}
          <div className="raw-section">
            <h3 className="section-subtitle">Markdown（生データ）</h3>
            <pre className="raw-content">
              <code>{result.content}</code>
            </pre>
          </div>

          {/* 関連画像表示 */}
          {result.images && result.images.length > 0 && (
            <div className="images-section">
              <h3 className="section-subtitle">関連画像</h3>
              <div className="images-grid">
                {result.images.map((image, index) => (
                  <div key={index} className="image-card">
                    <img 
                      src={image.url} 
                      alt={image.alt} 
                      loading="lazy"
                    />
                    <div className="image-credit">{image.credit}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {/* 投稿モーダル */}
        {publishModalOpen && (
          <div className="publish-modal-overlay" onClick={(e) => e.stopPropagation()}>
            <div className="publish-modal-container">
              <div className="publish-modal-header">
                <h3>記事を投稿</h3>
                <button 
                  className="close-button"
                  onClick={() => setPublishModalOpen(false)}
                >
                  <X size={18} />
                </button>
              </div>
              
              <div className="publish-modal-content">
                <div className="form-group">
                  <label htmlFor="article-title">記事タイトル</label>
                  {result?.suggested_title && (
                    <div className="suggested-title-info">
                      <small>💡 AI生成された推奨タイトル</small>
                    </div>
                  )}
                  <input
                    type="text"
                    id="article-title"
                    value={articleTitle}
                    onChange={(e) => setArticleTitle(e.target.value)}
                    placeholder="記事のタイトルを入力..."
                    required
                  />
                  {result?.suggested_title && result.suggested_title !== articleTitle && (
                    <button
                      type="button"
                      className="use-suggested-title-btn"
                      onClick={() => setArticleTitle(result.suggested_title)}
                    >
                      推奨タイトルを使用
                    </button>
                  )}
                </div>
                
                <div className="form-group">
                  <label>投稿先を選択</label>
                  <div className="platform-options">
                    {platforms.map((platform) => (
                      <label key={platform.id} className="platform-option">
                        <input
                          type="radio"
                          name="platform"
                          value={platform.id}
                          checked={selectedPlatform === platform.id}
                          onChange={(e) => setSelectedPlatform(e.target.value)}
                        />
                        <span className="platform-info">
                          <strong>{platform.name}</strong>
                          <small>{platform.description}</small>
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
                
                <div className="publish-modal-actions">
                  <button
                    className="cancel-button"
                    onClick={() => setPublishModalOpen(false)}
                  >
                    キャンセル
                  </button>
                  <button
                    className="publish-submit-button"
                    onClick={handlePublish}
                    disabled={!articleTitle.trim() || isPublishing}
                  >
                    {isPublishing ? '投稿中...' : '投稿する'}
                  </button>
                </div>
                
                {publishResult && (
                  <div className={`publish-result ${publishResult.success ? 'success' : 'error'}`}>
                    <p>{publishResult.message}</p>
                    {publishResult.instructions && (
                      <pre className="instructions">{publishResult.instructions}</pre>
                    )}
                    {publishResult.url && (
                      <p>
                        <a href={publishResult.url} target="_blank" rel="noopener noreferrer">
                          {publishResult.manual_mode ? 'noteで投稿する' : '投稿を確認する'}
                        </a>
                      </p>
                    )}
                    {publishResult.manual_mode && (
                      <div className="manual-copy-buttons">
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(publishResult.title);
                            alert('タイトルをコピーしました');
                          }}
                        >
                          タイトルをコピー
                        </button>
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(publishResult.content);
                            alert('本文をコピーしました');
                          }}
                        >
                          本文をコピー
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ResultModal;