"""
RAG (Retrieval-Augmented Generation) Pipeline
- Chunks financial data into text segments
- Creates embeddings via OpenAI API
- Stores/retrieves from FAISS vector store
- Generates LLM responses with retrieved context
"""
import os
import json
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from openai import OpenAI

# In-memory storage for FAISS indices and chunks per file
_indices = {}   # file_id -> faiss.IndexFlatL2
_chunks = {}    # file_id -> list of text chunks

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

EMBEDDING_MODEL = "text-embedding-ada-002"
CHAT_MODEL = "gpt-3.5-turbo"
EMBEDDING_DIM = 1536  # ada-002 dimension


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


def create_embeddings(chunks):
    """
    Create embeddings for text chunks using OpenAI API.

    Args:
        chunks: list of text strings

    Returns:
        numpy array of embeddings (n_chunks x embedding_dim)
    """
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=chunks
        )
        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings, dtype=np.float32)
    except Exception as e:
        print(f"⚠️ Embedding error: {e}")
        # Return random embeddings as fallback (for when API key is not set)
        return np.random.rand(len(chunks), EMBEDDING_DIM).astype(np.float32)


def store_embeddings(file_id, chunks, embeddings=None):
    """
    Store embeddings in FAISS index.

    Args:
        file_id: the file ID
        chunks: list of text chunks
        embeddings: optional pre-computed embeddings
    """
    if embeddings is None:
        embeddings = create_embeddings(chunks)

    _chunks[file_id] = chunks

    if FAISS_AVAILABLE:
        index = faiss.IndexFlatL2(EMBEDDING_DIM)
        index.add(embeddings)
        _indices[file_id] = index
    else:
        # Fallback: store raw embeddings
        _indices[file_id] = embeddings

    print(f"✅ Stored {len(chunks)} chunks for file {file_id}")


def retrieve_context(file_id, query, top_k=3):
    """
    Retrieve the most relevant chunks for a query.

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

    # Create query embedding
    query_embedding = create_embeddings([query])

    if FAISS_AVAILABLE and file_id in _indices:
        index = _indices[file_id]
        distances, indices_arr = index.search(query_embedding, min(top_k, len(chunks)))
        results = [chunks[i] for i in indices_arr[0] if i < len(chunks)]
    else:
        # Fallback: simple cosine similarity
        stored = _indices.get(file_id)
        if stored is not None and isinstance(stored, np.ndarray):
            # Cosine similarity
            norms_q = np.linalg.norm(query_embedding, axis=1, keepdims=True)
            norms_s = np.linalg.norm(stored, axis=1, keepdims=True)
            norms_q[norms_q == 0] = 1
            norms_s[norms_s == 0] = 1
            similarity = np.dot(query_embedding / norms_q, (stored / norms_s).T)
            top_indices = np.argsort(similarity[0])[::-1][:top_k]
            results = [chunks[i] for i in top_indices]
        else:
            results = chunks[:top_k]

    return results


def generate_response(query, context_chunks):
    """
    Generate an LLM response using retrieved context.

    Args:
        query: user question
        context_chunks: list of relevant text chunks

    Returns:
        string response
    """
    context = "\n\n".join(context_chunks)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a financial analyst AI assistant. Use the provided context to answer "
                "questions about the company's financial data. Be specific, use numbers from the "
                "context, and provide clear insights. If the context doesn't contain enough "
                "information, say so honestly."
            ),
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
        return f"AI response error: {str(e)}. Please check your OpenAI API key."


def build_rag_index(file_id, financial_data, raw_text=""):
    """
    Full RAG pipeline: chunk → embed → store.

    Args:
        file_id: the file ID
        financial_data: list of dicts with year, revenue, profit
        raw_text: raw extracted text
    """
    chunks = chunk_data(financial_data, raw_text)
    embeddings = create_embeddings(chunks)
    store_embeddings(file_id, chunks, embeddings)
    return chunks
