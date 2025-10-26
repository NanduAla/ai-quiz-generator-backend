// frontend/src/components/QuizDisplay.jsx
import React, { useState, useEffect } from 'react';

function QuizQuestion({ questionData, index, handleAnswer }) {
  const [selectedOption, setSelectedOption] = useState(null);
  const [showAnswer, setShowAnswer] = useState(false);

  const handleClick = (option) => {
    if (!showAnswer) {
      setSelectedOption(option);
      setShowAnswer(true);
      handleAnswer(option === questionData.answer);
    }
  };

  return (
    <div
      className={`p-4 mb-4 bg-white rounded-lg shadow-sm border border-gray-100 transition-all duration-500 transform ${
        showAnswer ? 'scale-105 shadow-lg' : ''
      }`}
    >
      <h4 className="text-xl font-semibold text-gray-800 mb-3">
        {index + 1}. {questionData.question}
      </h4>
      <div className="space-y-2 mb-4">
        {questionData.options.map((option, optIndex) => {
          const isCorrect = option === questionData.answer;
          const isSelected = option === selectedOption;
          return (
            <p
              key={optIndex}
              onClick={() => handleClick(option)}
              className={`p-2 rounded-md cursor-pointer transition duration-300 font-medium ${
                showAnswer
                  ? isCorrect
                    ? 'bg-green-200 border-l-4 border-green-500 text-green-700 animate-pulse'
                    : isSelected
                    ? 'bg-red-200 border-l-4 border-red-500 text-red-700 line-through'
                    : 'bg-gray-50 text-gray-400'
                  : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
              }`}
            >
              {option}
            </p>
          );
        })}
      </div>

      <button
        onClick={() => setShowAnswer(!showAnswer)}
        className="text-sm font-medium text-blue-600 hover:text-blue-800"
      >
        {showAnswer ? 'Hide Answer/Explanation' : 'Show Answer & Explanation'}
      </button>

      {showAnswer && (
        <div className="mt-3 p-3 border-t border-blue-200 space-y-1 bg-blue-50 rounded-b-lg text-sm transition-opacity duration-500 opacity-100">
          <p>
            <strong>Correct Answer:</strong>{' '}
            <span className="text-green-600">{questionData.answer}</span>
          </p>
          <p>
            <strong>Difficulty:</strong>{' '}
            <span className="capitalize font-semibold">{questionData.difficulty}</span>
          </p>
          <p>
            <strong>Explanation:</strong> {questionData.explanation}
          </p>
        </div>
      )}
    </div>
  );
}

export default function QuizDisplay({ quizData }) {
  const [score, setScore] = useState(0);
  const [answeredCount, setAnsweredCount] = useState(0);

  if (!quizData || !quizData.quiz || quizData.quiz.length === 0) {
    if (quizData) {
      return (
        <div className="p-4 bg-yellow-100 text-yellow-800 rounded-lg mt-6">
          <p>
            Quiz metadata was generated, but the LLM failed to produce any questions. Try a different article.
          </p>
        </div>
      );
    }
    return null;
  }

  const { title, summary, key_entities, quiz, related_topics } = quizData;

  // Ensure minimum 10 questions
  const quizList = quiz.slice(0, 10);

  const handleAnswer = (isCorrect) => {
    if (isCorrect) setScore((prev) => prev + 1);
    setAnsweredCount((prev) => prev + 1);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow-lg border-t-4 border-indigo-500">
        <h2 className="text-3xl font-extrabold text-indigo-700 mb-2">{title}</h2>
        <p className="text-gray-600 italic border-b pb-4 mb-4 text-sm">
          <strong>Summary:</strong> {summary}
        </p>
        <div className="text-right text-gray-700 font-semibold">
          Score: <span className="text-indigo-600 font-bold">{score}</span> / {quizList.length}
        </div>
      </div>

      {/* Quiz Questions */}
      <div className="bg-gray-50 p-6 rounded-lg shadow-lg">
        <h3 className="text-2xl font-bold text-gray-700 mb-4">Questions ({quizList.length})</h3>
        <div className="space-y-4">
          {quizList.map((question, index) => (
            <QuizQuestion key={index} questionData={question} index={index} handleAnswer={handleAnswer} />
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
