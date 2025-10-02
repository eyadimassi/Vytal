# src/chatbot/chain.py

import os
from dotenv import load_dotenv
from typing import List, Dict

# Import LangChain components for Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import our MedlinePlus API client
from src.medline_client.api import search_medlineplus

# --- 1. Load Environment Variables ---
# This loads the GOOGLE_API_KEY from your .env file.
load_dotenv()

# --- 2. Initialize the Language Model (Gemini) ---
# We initialize the ChatGoogleGenerativeAI model. "gemini-1.5-flash" is a fast
# and capable model available in the free tier.
# The temperature is set low for more factual, less creative outputs.
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)


# --- 3. Define the Prompt for Generating the Search Term ---
# This prompt template instructs the LLM to extract the most relevant
# medical term from the user's question.
search_query_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
    Based on the user's question below, what is the most relevant and concise 
    medical search term to look up in a health encyclopedia? 
    
    Return only the single search term and nothing else.

    Question: {question}
    Search Term:
    """
)

# --- 4. Define the Prompt for Generating the Final Answer ---
# This is the main prompt. It takes the retrieved MedlinePlus context and the
# original question and instructs the LLM to act as a helpful assistant,
# answering the question based ONLY on the provided context.
final_answer_prompt = PromptTemplate(
    input_variables=["question", "context"],
    template="""
    You are a helpful medical information assistant. Your role is to answer the user's 
    question based *only* on the trusted context provided below from MedlinePlus.

    - If the context does not contain the answer, state that you cannot find the information in the provided context.
    - Be clear, concise, and easy to understand.
    - Do not add any information that is not present in the context.

    CONTEXT FROM MEDLINEPLUS:
    -------------------------
    {context}
    -------------------------

    USER'S QUESTION: {question}

    ANSWER:
    """
)


def get_chatbot_response(user_question: str) -> str:
    """
    Orchestrates the entire process of generating a response to a user's question.

    Args:
        user_question (str): The question asked by the user.

    Returns:
        str: The generated answer.
    """
    # --- Part 1: Create a chain to generate the search query ---
    search_query_chain = search_query_prompt | llm | StrOutputParser()
    
    print(f"Original question: '{user_question}'")
    search_term = search_query_chain.invoke({"question": user_question})
    print(f"Generated search term: '{search_term}'")

    # --- Part 2: Retrieve data from MedlinePlus using our client ---
    search_results = search_medlineplus(search_term)

    if not search_results:
        return "I'm sorry, but I couldn't find any information on that topic in the MedlinePlus database."

    # --- Part 3: Format the search results into a single context string ---
    context = ""
    for result in search_results:
        context += f"Topic: {result['title']}\nSummary: {result['summary']}\n\n"
    
    print("--- Retrieved Context ---")
    print(context)
    print("-------------------------")

    # --- Part 4: Create the final chain to generate the answer ---
    answer_generation_chain = final_answer_prompt | llm | StrOutputParser()

    final_answer = answer_generation_chain.invoke({
        "question": user_question,
        "context": context
    })

    return final_answer


# --- Example of how to test this file directly ---
if __name__ == '__main__':
    print("Testing the chatbot chain with Google Gemini...")
    
    # Test Case 1: A common medical question
    test_question_1 = "What are the main symptoms of adult-onset asthma?"
    response_1 = get_chatbot_response(test_question_1)
    print("\n--- FINAL RESPONSE 1 ---")
    print(response_1)
    print("="*50)

    # Test Case 2: A question about a specific condition
    test_question_2 = "Tell me about psoriasis"
    response_2 = get_chatbot_response(test_question_2)
    print("\n--- FINAL RESPONSE 2 ---")
    print(response_2)
    print("="*50)
    
    # Test Case 3: A question that might not have a direct answer
    test_question_3 = "How much does brain surgery cost?"
    response_3 = get_chatbot_response(test_question_3)
    print("\n--- FINAL RESPONSE 3 ---")
    print(response_3)
    print("="*50)