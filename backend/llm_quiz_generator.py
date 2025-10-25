# backend/llm_quiz_generator.py

import os
import json
from dotenv import load_dotenv # ADDED: To ensure environment vars are loaded

from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# Local modules
from models import QuizOutput # Import the Pydantic schema

# --- Configuration & Initialization ---
GEMINI_MODEL = "gemini-2.5-flash"

# Load environment variables here (since this file is imported)
load_dotenv() 

# CORRECTED: Get the key by its variable name from the environment
API_KEY = os.getenv("GEMINI_API_KEY") 

if not API_KEY:
    # Use the correct variable name in the error message
    raise ValueError("GEMINI_API_KEY environment variable not set. Cannot initialize LLM.")
    
# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL, 
    temperature=0.2,
    # Explicitly pass the key (optional, but good practice)
    google_api_key=API_KEY 
)

# Get the Pydantic schema structure as a JSON string for the prompt
# This is crucial for guiding the LLM to output valid JSON
parser = JsonOutputParser(pydantic_object=QuizOutput)
format_instructions = parser.get_format_instructions()

# --- The Core Prompt Template ---
# This prompt is designed to instruct the LLM precisely on the task, 
# the source content, and the required output format.
PROMPT_TEMPLATE = """
You are an expert educational quiz generator AI. Your task is to analyze the provided text from a Wikipedia article and generate a structured, engaging quiz.

RULES:
1. **Quiz Length:** Generate exactly 5 to 10 unique, multiple-choice questions.
2. **Factual Grounding:** All answers, options, and explanations MUST be directly verifiable from the provided TEXT. Do not hallucinate or use external knowledge.
3. **Difficulty:** Include a mix of 'easy', 'medium', and 'hard' questions based on the depth of the text.
4. **Format:** You MUST adhere strictly to the JSON schema provided below. DO NOT add any extra text or markdown outside of the JSON block.

PROVIDED ARTICLE TEXT:
---
{article_content}
---

JSON OUTPUT SCHEMA INSTRUCTIONS:
{format_instructions}

Generate the JSON now:
"""

prompt = PromptTemplate(
    template=PROMPT_TEMPLATE,
    input_variables=["article_content"],
    partial_variables={"format_instructions": format_instructions}
)

# Create the LangChain processing chain
llm_quiz_chain = prompt | llm | parser

def generate_quiz_data(article_content: str) -> dict:
    """
    Runs the LLM chain to generate the structured quiz data.

    Args:
        article_content: The clean text content scraped from the Wikipedia article.

    Returns:
        A dictionary matching the QuizOutput Pydantic schema.
    """
    try:
        # The chain executes the prompt formatting, calls the LLM, and parses the JSON
        result = llm_quiz_chain.invoke({"article_content": article_content})
        
        # Validate the output against the Pydantic model again for safety
        QuizOutput(**result) 
        
        return result

    except Exception as e:
        print(f"LLM Generation Error: {e}")
        # In a real app, you would log this and return a structured error response
        raise RuntimeError(f"Failed to generate quiz from LLM: {e}")