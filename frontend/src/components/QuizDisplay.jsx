// frontend/src/components/QuizDisplay.jsx
import React, { useState } from 'react';

// Helper component for a single question
function QuizQuestion({ questionData, index }) {
  const [showAnswer, setShowAnswer] = useState(false);

  return (
    <div className="p-4 mb-4 bg-white rounded-lg shadow-sm border border-gray-100">
      <h4 className="text-xl font-semibold text-gray-800 mb-3">
        {index + 1}. {questionData.question}
      </h4>
      <div className="space-y-2 mb-4">
        {questionData.options.map((option, optIndex) => (
          <p 
            key={optIndex} 
            className={`p-2 rounded-md transition duration-150 text-sm ${
                showAnswer && option === questionData.answer 
                ? 'bg-green-100 border-l-4 border-green-500 text-green-700 font-medium' 
                : 'bg-gray-50 text-gray-700'
            }`}
          >
            {option}
          </p>
        ))}
      </div>
      
      <button 
        onClick={() => setShowAnswer(!showAnswer)}
        className="text-sm font-medium text-blue-600 hover:text-blue-800"
      >
        {showAnswer ? 'Hide Answer/Explanation' : 'Show Answer & Explanation'}
      </button>

      {showAnswer && (
        <div className="mt-3 p-3 border-t border-blue-200 space-y-1 bg-blue-50 rounded-b-lg text-sm">
          <p><strong>Correct Answer:</strong> <span className="text-green-600">{questionData.answer}</span></p>
          <p><strong>Difficulty:</strong> <span className="capitalize font-semibold">{questionData.difficulty}</span></p>
          <p><strong>Explanation:</strong> {questionData.explanation}</p>
        </div>
      )}
    </div>
  );
}


export default function QuizDisplay({ quizData }) {
    
    // 🛑 CRITICAL FIX: Guard Clause to prevent 'map' on undefined
    if (!quizData || !quizData.quiz || quizData.quiz.length === 0) {
        if (quizData) {
            // Data structure exists but quiz array is empty (e.g., LLM generation failure)
            return <div className="p-4 bg-yellow-100 text-yellow-800 rounded-lg mt-6">
                <p>Quiz metadata was generated, but the LLM failed to produce any questions. Try a different article.</p>
            </div>
        }
        return null; // Don't render anything if no data is present
    }

    const { title, summary, key_entities, quiz, related_topics } = quizData;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-white p-6 rounded-lg shadow-lg border-t-4 border-indigo-500">
                <h2 className="text-3xl font-extrabold text-indigo-700 mb-2">{title}</h2>
                <p className="text-gray-600 italic border-b pb-4 mb-4 text-sm">
                    <strong>Summary:</strong> {summary}
                </p>
            </div>

            {/* Quiz Questions */}
            <div className="bg-gray-50 p-6 rounded-lg shadow-lg">
                <h3 className="text-2xl font-bold text-gray-700 mb-4">Questions ({quiz.length})</h3>
                <div className="space-y-4">
                    {/* Safe mapping thanks to the guard clause above */}
                    {quiz.map((question, index) => (
                        <QuizQuestion key={index} questionData={question} index={index} />
                    ))}
                </div>
            </div>

            {/* Metadata */}
            <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-white p-6 rounded-lg shadow-lg">
                    <h4 className="text-xl font-bold text-gray-700 mb-2">Key Entities</h4>
                    <div className="text-sm text-gray-600 space-y-1">
                        <p><strong>People:</strong> {key_entities.people.join(', ') || 'N/A'}</p>
                        <p><strong>Organizations:</strong> {key_entities.organizations.join(', ') || 'N/A'}</p>
                        <p><strong>Locations:</strong> {key_entities.locations.join(', ')}</p>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-lg">
                    <h4 className="text-xl font-bold text-gray-700 mb-2">Related Topics</h4>
                    <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
                        {related_topics.map((topic, index) => (
                            <li key={index}>{topic}</li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
}