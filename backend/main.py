# backend/main.py
from dotenv import load_dotenv
load_dotenv() # CENTRALIZED: All environment variables loaded here first
# -----------------------------------------------------------------------
import json
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import exc as sqlalchemy_exc
from requests.exceptions import RequestException

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

# Initialize the database (creates tables if they don't exist)
init_db() 

# --- CORS Configuration (Example Code A) ---
origins = [
    "http://localhost:3000",  # Your React frontend's default port
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoint 0: Root/Health Check (Added to fix 404 on /) ---
@app.get("/")
def read_root():
    """Simple health check endpoint."""
    return {"message": "AI Wiki Quiz Generator API is Running! Use /generate_quiz or /history."}


# --- Endpoint 1: Generate Quiz (POST) ---
@app.post("/generate_quiz", response_model=QuizOutput, status_code=status.HTTP_201_CREATED)
def generate_quiz(url_input: URLInput, db: Session = Depends(get_db)):
    """
    Accepts a Wikipedia URL, scrapes, generates a quiz via LLM, and stores it in the DB.
    """
    url = str(url_input.url)
    
    # 1. Scrape Wikipedia
    try:
        clean_content, article_title = scrape_wikipedia(url)
    except (RequestException, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scraping failed for URL: {e}"
        )

    # 2. Generate Quiz Data via LLM
    try:
        quiz_data_dict = generate_quiz_data(article_content=clean_content)
    except RuntimeError as e:
        # Runtime Error handles the LLM failure from llm_quiz_generator.py
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation failed: {e}"
        )
        
    # Add non-LLM generated data to the final structure for return
    quiz_data_dict['url'] = url 
    quiz_data_dict['title'] = article_title 
    
    # 3. Store Data in Database
    try:
        # CRUCIAL: Serialize the complex JSON structure to a string for storage
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
        
        # Add the DB ID and date to the return object
        quiz_data_dict['id'] = db_quiz.id
        quiz_data_dict['date_generated'] = db_quiz.date_generated.isoformat()
        
    except sqlalchemy_exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database storage failed: {e}"
        )

    # 4. Return the full generated data
    return quiz_data_dict

# --- Endpoint 2: History (GET) ---
@app.get("/history")
def get_quiz_history(db: Session = Depends(get_db)):
    """
    Queries the database for a list of all saved quizzes (ID, URL, Title, Date).
    """
    quizzes = db.query(Quiz).order_by(Quiz.date_generated.desc()).all()
    
    # Format the data for a simple history list (id, url, title, date_generated)
    history_list = [
        {
            "id": q.id,
            "url": q.url,
            "title": q.title,
            "date_generated": q.date_generated.isoformat()
        }
        for q in quizzes
    ]
    return history_list

# --- Endpoint 3: Fetch Specific Quiz (/quiz/{quiz_id} GET) ---
@app.get("/quiz/{quiz_id}")
def get_single_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """
    Fetches a specific quiz record by ID and deserializes the quiz data.
    """
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if db_quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Quiz not found"
        )
    
    try:
        # CRUCIAL: Deserialize the full_quiz_data text field back into a dictionary/JSON object
        full_data = json.loads(db_quiz.full_quiz_data)
        
        # Add the record's primary fields back to the JSON structure
        full_data['id'] = db_quiz.id
        full_data['url'] = db_quiz.url
        full_data['date_generated'] = db_quiz.date_generated.isoformat()
        
        return full_data
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored quiz data is corrupted (invalid JSON format)."
        )