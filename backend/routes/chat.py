"""
Chat route — RAG-based chat with financial data.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.rag_pipeline import retrieve_context, generate_response, _chunks, build_rag_index
from database.models import (
    get_file, get_financial_data, insert_chat_message, get_chat_history
)

router = APIRouter()


class ChatRequest(BaseModel):
    file_id: int
    query: str
    eli15_mode: bool = False


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat with the financial data using RAG pipeline.
    Retrieves relevant context and generates AI response.
    Supports ELI5 (Explain Like I'm 5) mode for simplified explanations.
    """
    # Verify file exists
    file_record = get_file(request.file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Ensure RAG index exists
        if request.file_id not in _chunks:
            data = get_financial_data(request.file_id)
            if data:
                build_rag_index(request.file_id, data)
            else:
                return {"answer": "No financial data available for this file."}

        # Retrieve relevant context
        context_chunks = retrieve_context(request.file_id, request.query, top_k=5)

        # Generate AI response
        answer = generate_response(request.query, context_chunks, eli15_mode=request.eli15_mode)

        # Save chat messages to database
        insert_chat_message(request.file_id, "user", request.query)
        insert_chat_message(request.file_id, "assistant", answer)

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/chat/history/{file_id}")
async def get_chat_history_endpoint(file_id: int):
    """
    Retrieve full chat history for a file.
    Returns a list of messages with roles (user/assistant) and timestamps.
    """
    # Verify file exists
    file_record = get_file(file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        history = get_chat_history(file_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")
