# src/chatbot/retriever.py

import os
from typing import List

# --- CORRECTED IMPORTS ---
# BM25Retriever is a community component
from langchain_community.retrievers import BM25Retriever
# EnsembleRetriever is a core langchain component
from langchain.retrievers import EnsembleRetriever
# The rest of the imports are also corrected for modern versions
from langchain_cohere import CohereRerank
from langchain.retrievers import ContextualCompressionRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


def get_advanced_retriever(documents: List[Document]):
    """
    Creates and returns an advanced retriever using hybrid search and a reranker.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    splits = text_splitter.split_documents(documents)

    if not splits:
        return None

    bm25_retriever = BM25Retriever.from_documents(splits)
    bm25_retriever.k = 10

    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
    vectorstore = FAISS.from_documents(splits, embeddings)
    faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever],
        weights=[0.4, 0.6]
    )

    compressor = CohereRerank(
        model="rerank-english-v3.0",
        cohere_api_key=os.getenv("COHERE_API_KEY"),
        top_n=5
    )

    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=ensemble_retriever
    )

    return compression_retriever