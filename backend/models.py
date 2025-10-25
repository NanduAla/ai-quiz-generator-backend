# backend/models.py

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional

class QuizQuestion(BaseModel):
    """Defines the structure for a single quiz question."""
    question: str = Field(..., description="The text of the multiple-choice question.")
    options: List[str] = Field(..., description="A list of four possible answers (A, B, C, D).")
    answer: str = Field(..., description="The correct answer, must be one of the options.")
    difficulty: str = Field(..., description="The difficulty level, must be 'easy', 'medium', or 'hard'.")
    explanation: str = Field(..., description="A short explanation for the correct answer.")

class KeyEntities(BaseModel):
    """Defines the structure for key entities extracted from the article."""
    people: List[str] = Field(..., description="List of important people mentioned.")
    organizations: List[str] = Field(..., description="List of organizations or institutions.")
    locations: List[str] = Field(..., description="List of relevant locations.")

class QuizOutput(BaseModel):
    """The final, complete JSON structure returned by the LLM."""
    title: str = Field(..., description="The title of the Wikipedia article.")
    summary: str = Field(..., description="A concise summary of the article (max 3 sentences).")
    key_entities: KeyEntities
    sections: List[str] = Field(..., description="List of the main section headings used for content analysis.")
    quiz: List[QuizQuestion] = Field(..., min_length=5, max_length=10, description="A list of 5 to 10 generated quiz questions.")
    related_topics: List[str] = Field(..., description="Suggested Wikipedia topics for further reading based on the article.")

# --- Request Body for API ---
class URLInput(BaseModel):
    """Model for the API request body."""
    url: HttpUrl