# src/medline_client/api.py

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict
from bs4 import BeautifulSoup # <-- IMPORT BEAUTIFULSOUP

MEDLINEPLUS_API_URL = "https://wsearch.nlm.nih.gov/ws/query"

def search_medlineplus(query: str, retmax: int = 3) -> List[Dict[str, str]]:
    """
    Performs a live search on the MedlinePlus health topics database.
    This version now cleans HTML tags from the summary.
    """
    if not query:
        return []

    params = {
        'db': 'healthTopics',
        'term': query,
        'retmax': str(retmax)
    }

    try:
        # Increased timeout for more reliability
        response = requests.get(MEDLINEPLUS_API_URL, params=params, timeout=20)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        
        documents = []
        for doc in root.findall('.//document'):
            title_element = doc.find("content[@name='title']")
            summary_element = doc.find("content[@name='FullSummary']")
            
            if title_element is not None and summary_element is not None:
                # The title is usually clean, but we'll clean it just in case
                title_text = BeautifulSoup("".join(title_element.itertext()).strip(), "html.parser").get_text()
                
                # --- THIS IS THE KEY CHANGE ---
                # Get the raw summary text, which includes HTML
                raw_summary_text = "".join(summary_element.itertext()).strip()
                # Use BeautifulSoup to parse the HTML and get only the clean text
                clean_summary_text = BeautifulSoup(raw_summary_text, "html.parser").get_text()
                
                if title_text and clean_summary_text:
                    documents.append({
                        'title': title_text,
                        'summary': clean_summary_text
                    })
        
        print(f"--- MedlinePlus client found {len(documents)} documents for '{query}'.")
        return documents

    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        return []
    except ET.ParseError as e:
        print(f"XML Parsing Error: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []