import requests
from bs4 import BeautifulSoup
import json

def scrape_webpage(url):
    """
    Scrape the given webpage and return a JSON object containing the extracted data.
    
    Args:
        url (str): The URL of the webpage to scrape.
    
    Returns:
        dict: A dictionary containing the extracted data.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to retrieve the webpage: {e}"}

    soup = BeautifulSoup(response.text, 'html.parser')

    data = {
        "paragraphs": [paragraph.text for paragraph in soup.find_all('p')],
        "links": [link.get('href') for link in soup.find_all('a')],
        "images": [image.get('src') for image in soup.find_all('img')]
    }

    return data