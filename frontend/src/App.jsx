// frontend/src/App.jsx
import React, { useState, useCallback } from 'react';
import GenerateQuizTab from './tabs/GenerateQuizTab';
import HistoryTab from './tabs/HistoryTab';
import './index.css'; // Import Tailwind/custom styles

function App() {
  const [activeTab, setActiveTab] = useState('generate'); // 'generate' or 'history'
  const [quizData, setQuizData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Memoized handlers
  const onStartLoading = useCallback(() => setIsLoading(true), []);
  const onStopLoading = useCallback(() => setIsLoading(false), []);
  const setView = useCallback((viewName) => setActiveTab(viewName), []);

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-extrabold text-indigo-700">AI Wiki Quiz Generator</h1>
          <nav className="flex space-x-2">
            <button
              onClick={() => setActiveTab('generate')}
              className={`py-2 px-4 font-bold text-sm rounded-lg transition duration-150 border-2 ${
                activeTab === 'generate'
                  ? 'bg-indigo-600 text-white border-indigo-600 shadow-md'
                  : 'text-gray-600 border-gray-200 hover:bg-gray-100'
              }`}
            >
              Generate New Quiz
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`py-2 px-4 font-bold text-sm rounded-lg transition duration-150 border-2 ${
                activeTab === 'history'
                  ? 'bg-indigo-600 text-white border-indigo-600 shadow-md'
                  : 'text-gray-600 border-gray-200 hover:bg-gray-100'
              }`}
            >
              Quiz History
            </button>
          </nav>
        </div>
      </header>
      
      <main className="pb-12">
        {activeTab === 'generate' && (
          <GenerateQuizTab 
            quizData={quizData} 
            setQuizData={setQuizData}
            isLoading={isLoading}
            onStartLoading={onStartLoading}
            onStopLoading={onStopLoading}
          />
        )}
        {activeTab === 'history' && (
          <HistoryTab 
            setQuizData={setQuizData}
            setView={setView}
            isLoading={isLoading}
            onStartLoading={onStartLoading}
            onStopLoading={onStopLoading}
          />
        )}
      </main>
      
      {/* Global Loading Overlay */}
      {isLoading && (
          <div className="fixed inset-0 bg-black bg-opacity-20 flex items-center justify-center z-50">
             <div className="p-4 bg-white rounded-xl shadow-2xl flex items-center space-x-3">
                 <svg className="animate-spin h-6 w-6 text-indigo-600" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                 <p className="text-indigo-700 font-semibold">Loading...</p>
             </div>
          </div>
      )}
    </div>
  );
}

export default App;