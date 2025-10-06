# src/chatbot/chain.py

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
# NEW: We now import the reranker directly
from langchain_cohere import CohereRerank

# --- Custom Module Imports ---
from src.medline_client.api import search_medlineplus
from src.chatbot.memory import ConversationMemory

# --- 1. Load Environment Variables ---
load_dotenv()

# --- 2. Initialize LLM and Reranker ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
compressor = CohereRerank(
    model="rerank-english-v3.0",
    cohere_api_key=os.getenv("COHERE_API_KEY"),
    top_n=8  # We can increase this to get more diverse final results
)

# --- 3. Define Prompts ---

# NEW: This prompt now generates MULTIPLE search queries
search_query_template = """
Based on the user's question and conversation history below, generate a list of 3-5 concise, distinct medical search terms to look up in a health encyclopedia.
- Focus on different aspects of the user's query (e.g., symptoms, conditions, medical history).
- Return ONLY a comma-separated list of search terms.

PREVIOUS CONVERSATION:
{chat_history}

USER'S QUESTION: {question}

SEARCH TERMS:
"""
search_query_prompt = PromptTemplate.from_template(search_query_template)

# NEW: This prompt is enhanced to better handle follow-up questions
final_answer_template = """
You are Vytal, an expert AI health educator. Your persona is professional, empathetic, and clear.
Your primary mission is to synthesize the provided MedlinePlus context into a single, comprehensive, and easy-to-read response.

**Execution Rules:**

1.  **Analyze the Full Context:** Pay close attention to the `PREVIOUS CONVERSATION` to understand the user's full situation. If they ask a follow-up question like "what else could it be?", they are asking for alternative diagnoses for their *original symptoms*, not just things related to the last answer.

2.  **Direct Opening:** Begin the answer directly. **Do NOT** start with "Based on the provided context...".

3.  **Logical Structure & Formatting:**
    *   Analyze the user's question and the context to create logical sections.
    *   Use Markdown for clear formatting: `**Bold Headings**` for each section.
    *   Use bullet points (`-`) for lists.
    *   Ensure proper line breaks between paragraphs and headings.

4.  **Comprehensive Synthesis:**
    *   Combine information from all relevant context documents to form a complete picture. If there are multiple potential conditions, present them all.

5.  **Strict Context Adherence:**
    *   Your entire response must be based **exclusively** on the information within the `CONTEXT FROM MEDLINEPLUS` section.
    *   If the context does not contain an answer, you must explicitly state that.

6.  **Mandatory Disclaimer:**
    *   Conclude EVERY response with the mandatory medical disclaimer, visually separated by a horizontal line (`---`).

**PREVIOUS CONVERSATION:**
-------------------------
{chat_history}
-------------------------

**CONTEXT FROM MEDLINEPLUS:**
-------------------------
{context}
-------------------------

**USER'S QUESTION:** {question}

**YOUR EXPERT RESPONSE:**
"""
final_answer_prompt = PromptTemplate.from_template(final_answer_template)


# --- 4. Define the Main RAG Function (Completely Rewritten Logic) ---
def get_chatbot_response(user_question: str, memory: ConversationMemory) -> str:
    """
    Orchestrates an advanced RAG process with multi-query retrieval and direct reranking.
    """
    print(f"\nOriginal question: '{user_question}'")
    
    formatted_history = memory.get_formatted_history()

    # --- STAGE 1: MULTI-QUERY FETCHING ---
    search_query_chain = search_query_prompt | llm | StrOutputParser()
    search_queries_str = search_query_chain.invoke({
        "question": user_question,
        "chat_history": formatted_history
    })
    search_queries = [q.strip() for q in search_queries_str.split(',') if q.strip()]
    print(f"Generated search terms: {search_queries}")

    # Fetch documents for all queries and combine them, avoiding duplicates
    candidate_docs_raw = []
    seen_titles = set()
    for query in search_queries:
        docs = search_medlineplus(query, retmax=5) # Fetch 5 docs per query
        for doc in docs:
            if doc['title'] not in seen_titles:
                candidate_docs_raw.append(doc)
                seen_titles.add(doc['title'])

    if not candidate_docs_raw:
        return "I'm sorry, but I couldn't find any information on that topic in the MedlinePlus database."

    print(f"Fetched {len(candidate_docs_raw)} unique candidate documents from MedlinePlus.")
    candidate_docs = [
        Document(page_content=doc['summary'], metadata={'title': doc['title']})
        for doc in candidate_docs_raw
    ]

    # --- STAGE 2: DIRECT RERANKING (Faster!) ---
    # We no longer build a retriever. We rerank the fetched documents directly.
    reranked_results = compressor.compress_documents(candidate_docs, user_question)

    context = ""
    for doc in reranked_results:
        context += f"Topic: {doc.metadata['title']}\nSummary: {doc.page_content}\n\n"
    print("--- Reranked Context ---")
    print(context)
    print("------------------------")

    # --- STAGE 3: ANSWER GENERATION ---
    answer_generation_chain = final_answer_prompt | llm | StrOutputParser()
    final_answer = answer_generation_chain.invoke({
        "question": user_question,
        "context": context,
        "chat_history": formatted_history
    })

    return final_answer