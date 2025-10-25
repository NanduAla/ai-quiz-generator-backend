# backend/scraper.py

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

# Define a standard browser header
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def scrape_wikipedia(url: str) -> tuple[str, str]:
    """
    Fetches a Wikipedia URL, extracts the main article text, and the title.
    ...
    """
    try:
        # --- CRUCIAL CHANGE: Pass the HEAERS dictionary to the requests.get call ---
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
    except RequestException as e:
        raise RequestException(f"Failed to fetch URL: {e}")

    soup = BeautifulSoup(response.content, 'html.parser')

    # 1. Extract Article Title
    # Common Wikipedia title ID is 'firstHeading'
    title_tag = soup.find(id="firstHeading")
    article_title = title_tag.text if title_tag else "Unknown Title"

    # 2. Extract Main Content
    # The main article body is typically inside the div with id 'mw-content-text'
    content_div = soup.find(id="mw-content-text")
    if not content_div:
        raise ValueError("Could not find the main article content div on the page.")

    # 3. Clean Content
    
    # Target the primary parsed content within the main div
    main_body = content_div.find(class_="mw-parser-output")
    if not main_body:
        # Fallback to the whole content_div if specific parser output is missing
        main_body = content_div

    # List of elements to remove (boilerplate, references, navigation)
    for tag_name in ['table', 'dl', 'ul.vector-p-content-list', 'sup', 'style', 'script', 'nav', '.mw-editsection', '.reference', '.box-multiple-img', '.infobox']:
        for element in main_body.find_all(tag_name):
            element.decompose()
            
    # Extract all paragraph texts
    paragraphs = main_body.find_all('p', recursive=False)
    
    # Concatenate non-empty, stripped text from paragraphs
    clean_text_list = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    clean_text = "\n\n".join(clean_text_list)
    
    if not clean_text:
        raise ValueError("Scraped content is empty after cleaning. Check Wikipedia URL structure.")

    return clean_text, article_title