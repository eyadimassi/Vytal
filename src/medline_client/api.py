# src/medline_client/api.py

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict

MEDLINEPLUS_API_URL = "https://wsearch.nlm.nih.gov/ws/query"

def search_medlineplus(query: str, retmax: int = 3) -> List[Dict[str, str]]:
    """
    Performs a live search on the MedlinePlus health topics database.
    This version corrects the case-sensitive typo for the 'FullSummary' attribute.
    """
    if not query:
        return []

    params = {
        'db': 'healthTopics',
        'term': query,
        'retmax': str(retmax)
    }

    try:
        response = requests.get(MEDLINEPLUS_API_URL, params=params, timeout=10)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        
        documents = []
        for doc in root.findall('.//document'):
            title_element = doc.find("content[@name='title']")
            
            # --- THIS IS THE CORRECTED LINE ---
            # Changed 'fullSummary' to 'FullSummary' to match the XML attribute.
            summary_element = doc.find("content[@name='FullSummary']")
            
            if title_element is not None and summary_element is not None:
                title_text = "".join(title_element.itertext()).strip()
                summary_text = "".join(summary_element.itertext()).strip()
                
                if title_text and summary_text:
                    documents.append({
                        'title': title_text,
                        'summary': summary_text
                    })
        
        # This print statement is helpful for final confirmation
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
# --- New Test Block ---
# This allows us to test this file directly and isolate the API call
if __name__ == '__main__':
    print("--- Testing MedlinePlus API Client Directly ---")
    
    # Test with a very common term
    test_term = "Asthma"
    print(f"\nSearching for: '{test_term}'")
    results = search_medlineplus(test_term)
    
    if results:
        print("\n--- Search Successful ---")
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"  Title: {result['title']}")
            print(f"  Summary: {result['summary'][:100]}...") # Print first 100 chars
    else:
        print("\n--- Search Failed or Returned No Results ---")