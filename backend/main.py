"""
Financial Intelligence Copilot — Backend Entry Point
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from database.db import init_db
from routes.upload import router as upload_router
from routes.analysis import router as analysis_router
from routes.chat import router as chat_router
from routes.export import router as export_router

app = FastAPI(
    title="Financial Intelligence Copilot",
    description="AI-powered financial document analysis with RAG pipeline",
    version="1.0.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(upload_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(export_router, prefix="/api")


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)


@app.get("/")
async def root():
    return {"message": "Financial Intelligence Copilot API is running"}
