# src/chatbot/chain.py

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

# --- Custom Module Imports ---
from src.chatbot.retriever import get_advanced_retriever
from src.medline_client.api import search_medlineplus
from src.chatbot.memory import ConversationMemory

# --- 1. Load Environment Variables ---
load_dotenv()

# --- 2. Initialize the Language Model (Gemini) ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

# --- 3. Define Prompts (CORRECTED INITIALIZATION) ---

# Define the template string for the search query
search_query_template = """
Based on the user's question below, what is the most relevant and concise
medical search term to look up in a health encyclopedia?

Return only the single search term and nothing else.

Question: {question}
Search Term:
"""
# Create the prompt using the .from_template() method
search_query_prompt = PromptTemplate.from_template(search_query_template)


# Define the template string for the final answer
final_answer_template = """
You are a helpful medical information assistant. Your role is to answer the user's
question based only on the trusted context provided below from MedlinePlus.

- If the context does not contain the answer, state that you cannot find the information in the provided context.
- Be clear, concise, and easy to understand.
- Do not add any information that is not present in the context.
- Use the chat history to understand follow-up questions.

PREVIOUS CONVERSATION:
----------------------
{chat_history}
----------------------

CONTEXT FROM MEDLINEPLUS:
-------------------------
{context}
-------------------------

USER'S QUESTION: {question}

ANSWER:
"""
# Create the prompt using the .from_template() method
final_answer_prompt = PromptTemplate.from_template(final_answer_template)


# --- 4. Define the Main RAG Function ---
def get_chatbot_response(user_question: str, memory: ConversationMemory) -> str:
    """
    Orchestrates the RAG process using a dedicated memory object.
    
    Args:
        user_question: The user's latest question.
        memory: An instance of ConversationMemory containing the conversation history.

    Returns:
        The generated answer string.
    """
    print(f"\nOriginal question: '{user_question}'")

    # STAGE 1: CANDIDATE FETCHING
    search_query_chain = search_query_prompt | llm | StrOutputParser()
    search_term = search_query_chain.invoke({"question": user_question})
    print(f"Generated search term: '{search_term}'")

    candidate_docs_raw = search_medlineplus(search_term, retmax=15)
    if not candidate_docs_raw:
        return "I'm sorry, but I couldn't find any information on that topic in the MedlinePlus database."

    print(f"Fetched {len(candidate_docs_raw)} candidate documents from MedlinePlus.")
    candidate_docs = [
        Document(
            page_content=doc['summary'],
            metadata={'title': doc['title']}
        ) for doc in candidate_docs_raw
    ]

    # STAGE 2: ADVANCED RERANKING
    advanced_retriever = get_advanced_retriever(candidate_docs)
    if advanced_retriever is None:
        return "I'm sorry, but I couldn't process the information retrieved from MedlinePlus."
    
    reranked_results = advanced_retriever.invoke(user_question)
    context = ""
    for doc in reranked_results:
        context += f"Topic: {doc.metadata['title']}\nSummary: {doc.page_content}\n\n"
    print("--- Retrieved & Reranked Context ---")
    print(context)
    print("------------------------------------")
    
    # STAGE 3: ANSWER GENERATION
    formatted_history = memory.get_formatted_history()
    answer_generation_chain = final_answer_prompt | llm | StrOutputParser()
    final_answer = answer_generation_chain.invoke({
        "question": user_question,
        "context": context,
        "chat_history": formatted_history
    })

    return final_answer