"""
Chatbot service delegating to the unified Karran AI RAG & LLM Engine.
"""
from ai_assistant.rag_engine import ask_karran_ai


def ask_bot(question, lang="hi"):
    """
    Unified entrypoint for chatbot queries using RAG + LLM.
    """
    result = ask_karran_ai(question, user_lang=lang)
    return result.get("reply", "")