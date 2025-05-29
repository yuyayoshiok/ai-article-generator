// API設定
const API_BASE_URL = process.env.REACT_APP_API_URL || (
  process.env.NODE_ENV === 'production' 
    ? '' // 本番環境では相対URL（同一オリジン）
    : 'http://127.0.0.1:5001' // 開発環境ではローカルサーバー
);

export { API_BASE_URL };