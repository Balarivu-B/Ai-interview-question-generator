import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.routes import auth, questions, history, answers

root_path = ""

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for AI Interview Question Generator",
    version="1.0.0",
    root_path=root_path
)


# CORS configurations (for React frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. Adjust in production settings.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API V1 routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(questions.router, prefix=settings.API_V1_STR)
app.include_router(history.router, prefix=settings.API_V1_STR)
app.include_router(answers.router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "supabase_connected": settings.is_supabase_configured,
        "openai_connected": settings.is_openai_configured
    }
