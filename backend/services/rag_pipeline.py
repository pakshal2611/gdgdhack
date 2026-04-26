"""
RAG (Retrieval-Augmented Generation) Pipeline
- Chunks financial data into text segments
- Creates embeddings locally using TF-IDF (free, no API needed)
- Retrieves relevant chunks via cosine similarity
- Generates LLM responses with retrieved context via OpenRouter (free model)
"""
import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from openai import OpenAI

# In-memory storage for vectorizers, matrices, and chunks per file
_vectorizers = {}   # file_id -> TfidfVectorizer
_matrices = {}      # file_id -> TF-IDF sparse matrix
_chunks = {}        # file_id -> list of text chunks

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY", ""),
    timeout=60,          # 60-second timeout so it doesn't hang forever
    max_retries=1,
)

CHAT_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b:free")


def chunk_data(financial_data, raw_text=""):
    """
    Convert financial data and raw text into digestible text chunks for embedding.

    Args:
        financial_data: list of dicts with year, revenue, profit
        raw_text: raw extracted text from the document

    Returns:
        list of text chunks
    """
    chunks = []

    # Chunk 1: Overall summary
    if financial_data:
        summary_lines = ["Financial Data Summary:"]
        for row in financial_data:
            summary_lines.append(
                f"Year {row.get('year', 'N/A')}: Revenue = {row.get('revenue', 0):,.2f}, Profit = {row.get('profit', 0):,.2f}"
            )
        chunks.append("\n".join(summary_lines))

    # Chunk 2: Individual year data
    for row in financial_data:
        chunk = (
            f"In the year {row.get('year', 'N/A')}, "
            f"the company generated revenue of {row.get('revenue', 0):,.2f} "
            f"and profit of {row.get('profit', 0):,.2f}."
        )
        if row.get("revenue", 0) > 0:
            margin = (row.get("profit", 0) / row["revenue"]) * 100
            chunk += f" The profit margin was {margin:.1f}%."
        chunks.append(chunk)

    # Chunk 3: Growth analysis
    if len(financial_data) >= 2:
        for i in range(1, len(financial_data)):
            prev = financial_data[i - 1]
            curr = financial_data[i]
            if prev.get("revenue", 0) > 0:
                rev_growth = ((curr.get("revenue", 0) - prev["revenue"]) / prev["revenue"]) * 100
                chunks.append(
                    f"From {prev.get('year', 'N/A')} to {curr.get('year', 'N/A')}, "
                    f"revenue changed by {rev_growth:.1f}%."
                )
            if prev.get("profit", 0) > 0:
                prof_growth = ((curr.get("profit", 0) - prev["profit"]) / prev["profit"]) * 100
                chunks.append(
                    f"From {prev.get('year', 'N/A')} to {curr.get('year', 'N/A')}, "
                    f"profit changed by {prof_growth:.1f}%."
                )

    # Chunk 4: Raw text chunks (split into ~500 char pieces)
    if raw_text:
        text_chunks = _split_text(raw_text, max_length=500)
        chunks.extend(text_chunks)

    return chunks if chunks else ["No financial data available."]


def _split_text(text, max_length=500):
    """Split text into chunks of approximately max_length characters."""
    words = text.split()
    chunks = []
    current = []
    current_len = 0

    for word in words:
        if current_len + len(word) + 1 > max_length and current:
            chunks.append(" ".join(current))
            current = [word]
            current_len = len(word)
        else:
            current.append(word)
            current_len += len(word) + 1

    if current:
        chunks.append(" ".join(current))

    return chunks


def create_embeddings(file_id, chunks):
    """
    Create TF-IDF embeddings for text chunks (local, free, instant).

    Args:
        file_id: the file ID
        chunks: list of text strings

    Returns:
        (TfidfVectorizer, sparse TF-IDF matrix)
    """
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(chunks)
    return vectorizer, tfidf_matrix


def store_embeddings(file_id, chunks, vectorizer=None, tfidf_matrix=None):
    """
    Store TF-IDF vectorizer and matrix in memory.

    Args:
        file_id: the file ID
        chunks: list of text chunks
        vectorizer: fitted TfidfVectorizer
        tfidf_matrix: TF-IDF sparse matrix
    """
    _chunks[file_id] = chunks

    if vectorizer is not None and tfidf_matrix is not None:
        _vectorizers[file_id] = vectorizer
        _matrices[file_id] = tfidf_matrix
    else:
        v, m = create_embeddings(file_id, chunks)
        _vectorizers[file_id] = v
        _matrices[file_id] = m

    print(f"[OK] Stored {len(chunks)} chunks for file {file_id}")


def retrieve_context(file_id, query, top_k=3):
    """
    Retrieve the most relevant chunks for a query using TF-IDF cosine similarity.

    Args:
        file_id: the file ID
        query: user query string
        top_k: number of chunks to retrieve

    Returns:
        list of relevant text chunks
    """
    if file_id not in _chunks:
        return ["No data available for this file."]

    chunks = _chunks[file_id]

    if file_id in _vectorizers and file_id in _matrices:
        vectorizer = _vectorizers[file_id]
        tfidf_matrix = _matrices[file_id]

        # Transform query using the same vectorizer
        query_vec = vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

        # Get top-k indices
        top_indices = similarities.argsort()[::-1][:top_k]
        results = [chunks[i] for i in top_indices if i < len(chunks)]
    else:
        # Fallback: return first chunks
        results = chunks[:top_k]

    return results


def generate_response(query, context_chunks, eli15_mode=False):
    """
    Generate an LLM response using retrieved context via OpenRouter (free model).

    Args:
        query: user question
        context_chunks: list of relevant text chunks
        eli15_mode: if True, use simplified ELI5 (Explain Like I'm 5) system prompt

    Returns:
        string response
    """
    context = "\n\n".join(context_chunks)

    # Select system prompt based on eli15_mode
    if eli15_mode:
        system_prompt = (
            "You are a financial analyst AI. Explain everything in very simple words that a "
            "15-year-old student could understand. Avoid all financial jargon. When you must "
            "use a financial term, immediately explain it in brackets in plain English. Use "
            "short sentences. Be friendly and clear."
        )
    else:
        system_prompt = (
            "You are a financial analyst AI assistant. Use the provided context to answer "
            "questions about the company's financial data. Be specific, use numbers from the "
            "context, and provide clear insights. If the context doesn't contain enough "
            "information, say so honestly."
        )

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {query}",
        },
    ]

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI response error: {str(e)}. Please check your OpenRouter API key."


def build_rag_index(file_id, financial_data, raw_text=""):
    """
    Full RAG pipeline: chunk → embed (TF-IDF) → store.

    Args:
        file_id: the file ID
        financial_data: list of dicts with year, revenue, profit
        raw_text: raw extracted text
    """
    chunks = chunk_data(financial_data, raw_text)
    vectorizer, tfidf_matrix = create_embeddings(file_id, chunks)
    store_embeddings(file_id, chunks, vectorizer, tfidf_matrix)
    return chunks
