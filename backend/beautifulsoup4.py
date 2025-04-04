import requests
from bs4 import BeautifulSoup
import json

# Modified scrape_webpage function to handle HTML content directly
def scrape_webpage(html_content):
    """
    Parse HTML content and extract structured data.
   
    Args:
        html_content (str): HTML content as a string.
   
    Returns:
        dict: A dictionary containing the extracted data.
    """
    try:
        # If input is a URL rather than HTML content, handle that case
        if isinstance(html_content, str) and (html_content.startswith('http://') or html_content.startswith('https://')):
            response = requests.get(html_content)
            response.raise_for_status()
            html_content = response.text
            
        # Create BeautifulSoup object from HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract data
        data = {
            "paragraphs": [paragraph.text for paragraph in soup.find_all('p')],
            "links": [link.get('href') for link in soup.find_all('a')],
            "images": [image.get('src') for image in soup.find_all('img')]
        }
        return data
        
    except Exception as e:
        return {
            "paragraphs": [],
            "links": [],
            "images": [],
            "error": f"Failed to process HTML: {str(e)}"
        }