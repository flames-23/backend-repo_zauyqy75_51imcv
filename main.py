import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    topic: str


class QuizItem(BaseModel):
    q: str
    options: List[str]
    answer: int


class GenerateResponse(BaseModel):
    base: str
    subtopics: List[str]
    explanations: Dict[str, str]
    examples: Dict[str, List[str]]
    quizzes: Dict[str, List[QuizItem]]


def generate_content(topic: str) -> Dict[str, Any]:
    base = topic.strip() or "Introduction to Learning"

    # Create subtopics dynamically by mixing templates with the provided topic
    subtopics = [
        f"Foundations of {base}",
        f"Core Concepts in {base}",
        f"Applying {base}",
        f"Quick Review & Pitfalls",
    ]

    explanations = {
        subtopics[0]: f"Start with the fundamentals of {base}. Clarify definitions, the problem {base} tries to solve, and key terminology.",
        subtopics[1]: f"Dive into the main building blocks of {base}. Understand how ideas connect and compare trade-offs.",
        subtopics[2]: f"Practice using {base} in realistic scenarios. Work through step-by-step reasoning and examples.",
        subtopics[3]: f"Summarize what you've learned about {base}, highlight common mistakes, and create a concise review list.",
    }

    examples = {
        subtopics[0]: [
            f"Define {base} in one sentence.",
            f"List 3 real-world applications where {base} is useful.",
            f"Explain why {base} matters for learners at your level.",
        ],
        subtopics[1]: [
            f"Describe a core concept of {base} and give a short example.",
            f"Contrast two approaches used in {base} and when to pick each.",
            f"What assumptions are common when studying {base}?",
        ],
        subtopics[2]: [
            f"Walk through a worked example applying {base} step by step.",
            f"Identify edge cases that can break naive use of {base}.",
            f"Create a small challenge exercise involving {base}.",
        ],
        subtopics[3]: [
            f"Write a 5-bullet summary of {base}.",
            f"Name two common pitfalls and how to avoid them in {base}.",
            f"Draft 3 flashcards to remember key ideas in {base}.",
        ],
    }

    # Generate lightweight quizzes. Answers are deterministic to allow scoring client-side.
    quizzes: Dict[str, List[Dict[str, Any]]] = {
        subtopics[0]: [
            {
                "q": f"Which best describes the aim of {base}?",
                "options": [
                    "It replaces all prior knowledge",
                    "It provides a framework of key ideas",
                    "It is only a set of formulas",
                    "It has no practical use",
                ],
                "answer": 1,
            },
            {
                "q": f"A good first step when learning {base} is to:",
                "options": [
                    "Memorize random facts",
                    "Skim advanced papers",
                    "Clarify definitions and goals",
                    "Skip to hard problems",
                ],
                "answer": 2,
            },
        ],
        subtopics[1]: [
            {
                "q": f"Core concepts in {base} should be:",
                "options": [
                    "Learned in isolation only",
                    "Connected to each other",
                    "Ignored if difficult",
                    "Left for later",
                ],
                "answer": 1,
            },
            {
                "q": f"Trade-offs in {base} help you:",
                "options": [
                    "Pick approaches that fit the context",
                    "Avoid making choices",
                    "Always choose the most complex method",
                    "Ignore constraints",
                ],
                "answer": 0,
            },
        ],
        subtopics[2]: [
            {
                "q": f"When applying {base}, start by:",
                "options": [
                    "Writing code immediately",
                    "Understanding the problem and constraints",
                    "Skipping examples",
                    "Only reading theory",
                ],
                "answer": 1,
            },
            {
                "q": f"Edge cases are important because they:",
                "options": [
                    "Never occur",
                    "Make solutions more entertaining",
                    "Reveal hidden assumptions",
                    "Reduce clarity",
                ],
                "answer": 2,
            },
        ],
        subtopics[3]: [
            {
                "q": f"A concise review of {base} should:",
                "options": [
                    "List key points and pitfalls",
                    "Introduce unrelated topics",
                    "Avoid structure",
                    "Be overly long",
                ],
                "answer": 0,
            },
            {
                "q": f"Flashcards for {base} work best when they:",
                "options": [
                    "Ask clear, focused questions",
                    "Contain essays",
                    "Use only images",
                    "Avoid spaced repetition",
                ],
                "answer": 0,
            },
        ],
    }

    return {
        "base": base,
        "subtopics": subtopics,
        "explanations": explanations,
        "examples": examples,
        "quizzes": quizzes,
    }


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.post("/api/generate", response_model=GenerateResponse)
def generate_endpoint(payload: GenerateRequest):
    topic = (payload.topic or "").strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")
    data = generate_content(topic)
    return data


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
