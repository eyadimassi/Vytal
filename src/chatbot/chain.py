# backend-python/src/chatbot/chain.py

import os
import logging  
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# --- AGENT IMPORTS ---
from langchain.agents import AgentExecutor, create_react_agent, Tool
from langchain_tavily import TavilySearch

# --- Custom Module Imports ---
from src.medline_client.api import search_medlineplus
from src.chatbot.memory import ConversationMemory

load_dotenv()


llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)


def run_medline_search(query: str) -> str:
    
    logging.info(f"--- Executing MedlinePlus Search Tool with query: '{query}' ---")
    docs = search_medlineplus(query, retmax=5)
    if not docs:
        return "No relevant information found in the MedlinePlus encyclopedia."
    
    context = ""
    for doc in docs:
        context += f"Topic: {doc['title']}\nSummary: {doc['summary']}\n\n"
    return context

medline_tool = Tool(
    name="MedlinePlus_Search",
    func=run_medline_search,
    description="""
    Use this tool FIRST to find trusted medical information.
    It is an encyclopedia covering diseases, conditions, symptoms, medical tests, and treatments.
    It is the best source for established medical knowledge.
    """
)


tavily_search = TavilySearch(max_results=5)
web_search_tool = Tool(
    name="tavily_search_results_json",
    func=tavily_search.invoke,
    description="""
    Use this tool as a FALLBACK if the MedlinePlus_Search tool returns no results or insufficient information.
    It is useful for very recent medical news, new drug approvals, clinical trials, or topics not found in a medical encyclopedia.
    """
)

tools = [medline_tool, web_search_tool]


system_message = """
You are Vytal, an expert AI health educator. Your persona is professional, empathetic, and clear.
Your primary mission is to answer the user's question by using the available tools.

**Execution Rules:**
1.  **Prioritize MedlinePlus:** You MUST use the `MedlinePlus_Search` tool first for any medical query.
2.  **Fallback to Web Search:** Only if the `MedlinePlus_Search` tool returns "No relevant information found" or the information is clearly insufficient, you should then use the `tavily_search_results_json` tool.
3.  **Synthesize:** Combine the information from the tools to form a single, comprehensive, and easy-to-read response.
4.  **Formatting:** Use Markdown for clear formatting: `**Bold Headings**` and bullet points (`-`).
5.  **Disclaimer:** Conclude EVERY response with the mandatory medical disclaimer, visually separated by a horizontal line (`---`).

---
MANDATORY DISCLAIMER:
I am an AI assistant and not a medical professional. This information is for educational purposes only. Please consult with a qualified healthcare provider for any medical advice, diagnosis, or treatment.
---

TOOLS:
------
You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question
"""

agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = create_react_agent(llm=llm, tools=tools, prompt=agent_prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5
)


def get_chatbot_response(user_question: str, memory: ConversationMemory) -> str:
    
    logging.info(f"--- New Request --- User Question: '{user_question}'")
    
    chat_history = memory.get_langchain_history()

    try:
        response = agent_executor.invoke({
            "input": user_question,
            "chat_history": chat_history
        })
        return response['output']
    except Exception as e:
        
        logging.exception("--- ERROR DURING AGENT EXECUTION ---")
        return "I'm sorry, but I encountered an error while processing your request. Please check my logs or try again."