// frontend/src/tabs/GenerateQuizTab.jsx
import React, { useState } from 'react';
import QuizDisplay from '../components/QuizDisplay';
import { generateQuiz } from '../services/api';

export default function GenerateQuizTab({ quizData, setQuizData, onStartLoading, onStopLoading, isLoading }) {
  const [url, setUrl] = useState('');
  const [error, setError] = useState(null);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!url) {
      setError("Please enter a Wikipedia URL.");
      return;
    }
    
    onStartLoading();
    setError(null);
    setQuizData(null); // Clear previous quiz

    try {
      const data = await generateQuiz(url);
      setQuizData(data);
      setUrl(''); // Clear the URL input
    } catch (err) {
      console.error("Quiz Generation Error:", err);
      setError(`Failed to generate quiz: ${err.message}. Check your FastAPI server and API key.`);
    } finally {
      onStopLoading();
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <form onSubmit={handleGenerate} className="flex space-x-2 mb-8 shadow-xl rounded-lg overflow-hidden">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste Wikipedia URL here..."
          disabled={isLoading}
          required
          className="flex-grow p-4 border-0 focus:ring-4 focus:ring-indigo-300 focus:ring-opacity-50 transition duration-150 text-gray-700"
        />
        <button 
          type="submit" 
          disabled={isLoading}
          className="px-6 py-4 bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition duration-150 disabled:bg-indigo-400"
        >
          {isLoading ? 'Generating Quiz...' : 'Generate Quiz'}
        </button>
      </form>

      {error && (
        <div className="p-4 mb-6 bg-red-100 border-l-4 border-red-500 text-red-700 rounded-lg" role="alert">
          <p className="font-medium">Error:</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {isLoading && !error && (
        <div className="text-center p-8 text-lg font-medium text-indigo-600 bg-white rounded-lg shadow-md">
            <svg className="animate-spin h-5 w-5 text-indigo-500 mr-3 inline-block" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            Processing article and generating quiz... (10-30 seconds)
        </div>
      )}

      <QuizDisplay quizData={quizData} />
    </div>
  );
}