from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from config import REQUEST_TIMEOUT, MAX_CONTENT_LENGTH
import re


def is_valid_url(url: str) -> bool:
    """Validate if a string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace."""
    return re.sub(r'\s+', ' ', text).strip()

def scrape_url(url: str) -> tuple[str, bool]:
    """
    Scrape content from a URL.
    
    Returns:
        tuple: (text content, success flag)
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=' ', strip=True)
        cleaned_text = clean_text(text[:MAX_CONTENT_LENGTH])
        
        return cleaned_text, True
    except requests.RequestException as e:
        return f"Error scraping the URL: {str(e)}", False
