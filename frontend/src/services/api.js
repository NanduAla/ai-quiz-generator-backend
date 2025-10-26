// frontend/src/services/api.js
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * Calls the FastAPI endpoint to generate a new quiz from a Wikipedia URL.
 */
export async function generateQuiz(url) {
  const response = await fetch(`${BACKEND_URL}/generate_quiz`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
  }

  return response.json();
}

/**
 * Calls the FastAPI endpoint to get the list of saved quizzes.
 */
export async function getQuizHistory() {
  const response = await fetch(`${BACKEND_URL}/history`);

  if (!response.ok) {
    throw new Error(`Failed to fetch history: ${response.status}`);
  }

  return response.json();
}

/**
 * Calls the FastAPI endpoint to fetch a single quiz by ID.
 */
export async function getSingleQuiz(quizId) {
  const response = await fetch(`${BACKEND_URL}/quiz/${quizId}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch quiz ID ${quizId}.`);
  }

  return response.json();
}