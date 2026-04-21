"""
AI Insights generator — uses RAG pipeline to generate financial summaries.
"""
from database.models import get_financial_data
from services.rag_pipeline import retrieve_context, generate_response, build_rag_index, _chunks


def generate_insights(file_id):
    """
    Generate a plain-English AI summary of financial performance.
    Uses the RAG pipeline to retrieve context and generate insights.

    Args:
        file_id: the file ID

    Returns:
        string — AI-generated insights
    """
    # Ensure RAG index exists for this file
    if file_id not in _chunks:
        data = get_financial_data(file_id)
        if data:
            # Build RAG index from stored data
            build_rag_index(file_id, data)
        else:
            return "No financial data available for analysis."

    query = (
        "Explain the company's financial performance in simple terms. "
        "Include key metrics like revenue trends, profit margins, and overall health. "
        "Highlight any significant changes or concerns."
    )

    # Retrieve relevant context
    context_chunks = retrieve_context(file_id, query, top_k=5)

    # Generate response
    insights = generate_response(query, context_chunks)

    return insights
