# backend-python/src/chatbot/chain.py

import os
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.prompts import MessagesPlaceholder

# AGENT IMPORTS
from langchain.agents import AgentExecutor, create_react_agent, Tool
from langchain import hub
from langchain_tavily import TavilySearch

# Custom Module Imports 
from src.medline_client.api import search_medlineplus
from src.chatbot.memory import ConversationMemory


load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)


def run_medline_search(query: str) -> str:
    logging.info(f"--- Executing MedlinePlus Search Tool with query: '{query}' ---")
    docs = search_medlineplus(query, retmax=3)
    if not docs:
        return "No relevant information found in the MedlinePlus encyclopedia."
    context = ""
    for doc in docs:
        context += f"Topic: {doc['title']}\nSummary: {doc['summary']}\n\n"
    return context

medline_tool = Tool(
    name="MedlinePlus_Search",
    func=run_medline_search,
    description="Use this tool FIRST to find trusted medical information about diseases, conditions, and wellness topics."
)

tavily_search = TavilySearch(max_results=3)
web_search_tool = Tool(
    name="Web_Search",
    func=lambda query: tavily_search.invoke(query),
    description="Use this tool as a FALLBACK only if MedlinePlus_Search returns no relevant information."
)

tools = [medline_tool, web_search_tool]


prompt = hub.pull("hwchase17/react-chat")


system_message = """You are Vytal, an expert AI health educator. Your persona is professional, empathetic, and clear.

Your mission is to provide a detailed and well-structured answer to the user's question using the available tools.

**RULES:**
1.  You **MUST** use the `MedlinePlus_Search` tool first for any medical query.
2.  You **MUST ONLY** use the `Web_Search` tool if the `MedlinePlus_Search` tool returns "No relevant information found".
3.  **Synthesize and Structure:** Do not just summarize. Create a detailed, easy-to-read response organized with clear headings (using `### Headings`) and bullet points. A good answer should explain what the condition is, list its primary symptoms in detail, and include a section on when it is important to seek medical attention.
4.  Conclude **EVERY** response with the mandatory medical disclaimer, separated by a horizontal line (`---`).

---
MANDATORY DISCLAIMER:
I am an AI assistant and not a medical professional. This information is for educational purposes only. Please consult with a qualified healthcare provider for any medical advice, diagnosis, or treatment.
---"""

prompt.template = system_message + "\n\n" + prompt.template

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10,
)

def get_chatbot_response(user_question: str, memory: ConversationMemory) -> str:
    logging.info(f"--- New Request --- User Question: '{user_question}'")
    chat_history = memory.get_langchain_history()
    try:
        response = agent_executor.invoke({
            "input": user_question,
            "chat_history": chat_history,
        })
        return response['output']
    except Exception:
        logging.exception("--- ERROR DURING AGENT EXECUTION ---")
        return "I'm sorry, but I encountered an error while processing your request. Please check the server logs for more details."