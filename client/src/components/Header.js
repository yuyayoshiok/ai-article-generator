import React from 'react';
import { FileText, Bot } from 'lucide-react';

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        {/* ロゴとタイトル */}
        <div className="logo-section">
          <div className="logo-icon">
            <Bot size={32} />
          </div>
          <div className="logo-text">
            <h1 className="app-title">記事生成ツール</h1>
            <p className="app-subtitle">AI powered writing assistant</p>
          </div>
        </div>
        
        {/* ヘッダーアイコン */}
        <div className="header-icon">
          <FileText size={28} />
        </div>
      </div>
    </header>
  );
}

export default Header;