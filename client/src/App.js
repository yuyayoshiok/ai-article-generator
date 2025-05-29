import React, { useState } from 'react';
import './App.css';
import GenerateTab from './components/GenerateTab';
import RewriteTab from './components/RewriteTab';
import { Sparkles, Edit3 } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('generate');

  return (
    <div className="App">
      <div className="container">
        <div className="tab-container">
          <div className="tab-buttons">
            <button 
              className={`tab-button ${activeTab === 'generate' ? 'active' : ''}`}
              onClick={() => setActiveTab('generate')}
            >
              <Sparkles size={20} />
              記事生成
            </button>
            <button 
              className={`tab-button ${activeTab === 'rewrite' ? 'active' : ''}`}
              onClick={() => setActiveTab('rewrite')}
            >
              <Edit3 size={20} />
              リライト
            </button>
          </div>
          
          <div className="tab-content">
            {activeTab === 'generate' ? <GenerateTab /> : <RewriteTab />}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;