from dotenv import load_dotenv
import os, json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

from database import get_db, init_db, Quiz
from models import URLInput, QuizOutput
from scraper import scrape_wikipedia
from llm_quiz_generator import generate_quiz_data

# Load .env locally; on Render, vars are in the environment
load_dotenv()

app = FastAPI(title="AI Wiki Quiz Generator")

# Initialize DB
init_db()

# CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL] if FRONTEND_URL != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/generate_quiz", response_model=QuizOutput)
def generate_quiz(url_input: URLInput, db: Session = Depends(get_db)):
    try:
        clean_content, article_title = scrape_wikipedia(url_input.url)
        quiz_data = generate_quiz_data(clean_content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save to DB (convert HttpUrl to string)
    try:
        db_quiz = Quiz(
            url=str(url_input.url),
            title=article_title,
            scraped_content=clean_content,
            full_quiz_data=json.dumps(quiz_data)
        )
        db.add(db_quiz)
        db.commit()
        db.refresh(db_quiz)
        quiz_data['id'] = db_quiz.id
        quiz_data['date_generated'] = db_quiz.date_generated.isoformat()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB Error: {e}")

    return quiz_data

@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).order_by(Quiz.date_generated.desc()).all()
    return [
        {
            "id": q.id,
            "title": q.title,
            "url": q.url,
            "date_generated": q.date_generated.isoformat()
        }
        for q in quizzes
    ]

@app.get("/quiz/{quiz_id}")
def get_single_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    data = json.loads(quiz.full_quiz_data)
    data.update({"id": quiz.id, "url": quiz.url, "date_generated": quiz.date_generated.isoformat()})
    return data

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render provides PORT
    uvicorn.run("main:app", host="0.0.0.0", port=port)
