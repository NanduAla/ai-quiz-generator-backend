from dotenv import load_dotenv
load_dotenv()
import os
import json
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import exc as sqlalchemy_exc
from requests.exceptions import RequestException
import uvicorn

# Local modules
from database import get_db, init_db, Quiz
from models import URLInput, QuizOutput
from scraper import scrape_wikipedia
from llm_quiz_generator import generate_quiz_data

# --- Initialization ---
app = FastAPI(
    title="AI Wiki Quiz Generator",
    description="Full-stack application using FastAPI, LangChain, and Gemini to create quizzes from Wikipedia URLs."
)

# Initialize database
init_db()

# --- CORS Configuration ---
frontend_url = os.environ.get("FRONTEND_URL")  # Set this in Render environment variables
origins = [
    "http://localhost:3000",
    "https://ai-quiz-generator-delta-nine.vercel.app"  # Your deployed frontend
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health Check ---
@app.get("/health")
def health_check():
    return {"status": "ok"}

# --- Generate Quiz ---
@app.post("/generate_quiz", response_model=QuizOutput, status_code=status.HTTP_201_CREATED)
def generate_quiz(url_input: URLInput, db: Session = Depends(get_db)):
    url = str(url_input.url)
    try:
        clean_content, article_title = scrape_wikipedia(url)
    except (RequestException, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Scraping failed: {e}")

    try:
        quiz_data_dict = generate_quiz_data(article_content=clean_content)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI generation failed: {e}")

    quiz_data_dict['url'] = url
    quiz_data_dict['title'] = article_title

    try:
        quiz_json_string = json.dumps(quiz_data_dict)
        db_quiz = Quiz(
            url=url,
            title=article_title,
            scraped_content=clean_content,
            full_quiz_data=quiz_json_string
        )
        db.add(db_quiz)
        db.commit()
        db.refresh(db_quiz)

        quiz_data_dict['id'] = db_quiz.id
        quiz_data_dict['date_generated'] = db_quiz.date_generated.isoformat()

    except sqlalchemy_exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database storage failed: {e}")

    return quiz_data_dict

# --- History ---
@app.get("/history")
def get_quiz_history(db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).order_by(Quiz.date_generated.desc()).all()
    return [
        {"id": q.id, "url": q.url, "title": q.title, "date_generated": q.date_generated.isoformat()}
        for q in quizzes
    ]

# --- Fetch Single Quiz ---
@app.get("/quiz/{quiz_id}")
def get_single_quiz(quiz_id: int, db: Session = Depends(get_db)):
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not db_quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    try:
        full_data = json.loads(db_quiz.full_quiz_data)
        full_data['id'] = db_quiz.id
        full_data['url'] = db_quiz.url
        full_data['date_generated'] = db_quiz.date_generated.isoformat()
        return full_data
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Stored quiz data is corrupted.")

# --- Run ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
