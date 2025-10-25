// frontend/src/tabs/HistoryTab.jsx
import React, { useState, useEffect, useCallback } from 'react';
import HistoryTable from '../components/HistoryTable';
import { getQuizHistory, getSingleQuiz } from '../services/api';

export default function HistoryTab({ setQuizData, setView, onStartLoading, onStopLoading, isLoading }) {
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);

  // Memoized fetch function for re-use
  const fetchHistory = useCallback(async () => {
    onStartLoading();
    setError(null);
    try {
      const data = await getQuizHistory();
      setHistory(data);
    } catch (err) {
      setError(`Error fetching history: ${err.message}`);
    } finally {
      onStopLoading();
    }
  }, [onStartLoading, onStopLoading]);

  // Initial data load
  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);


  const handleSelectQuiz = async (quizId) => {
    onStartLoading();
    setQuizData(null);
    setError(null);

    try {
      const data = await getSingleQuiz(quizId);
      setQuizData(data);
      setView('generate'); // Switch to the generate tab to show the selected quiz
    } catch (err) {
      setError(`Error fetching quiz ${quizId}: ${err.message}`);
    } finally {
      onStopLoading();
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Quiz History</h2>
        <HistoryTable 
            history={history} 
            isLoading={isLoading} 
            error={error} 
            onSelectQuiz={handleSelectQuiz} 
        />
        <div className="text-center mt-6">
             <button
                onClick={fetchHistory}
                disabled={isLoading}
                className="py-2 px-4 text-sm bg-gray-200 rounded-lg hover:bg-gray-300 transition disabled:opacity-50"
            >
                {isLoading ? 'Refreshing...' : 'Refresh History'}
            </button>
        </div>
    </div>
  );
}