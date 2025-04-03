import requests
from bs4 import BeautifulSoup

# Send a GET request to the webpage
url = "https://portfolio-jytw.vercel.app/"
response = requests.get(url)

# Check if the request was successful
if response.status_code != 200:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    exit(1)

# Parse the HTML content of the webpage using BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Now you can use BeautifulSoup methods to navigate and search the HTML content
# For example, to find all paragraph elements:
paragraphs = soup.find_all('p')
for paragraph in paragraphs:
    print(paragraph.text)

# To find all links:
links = soup.find_all('a')
for link in links:
    print(link.get('href'))

# To find all images:
images = soup.find_all('img')
for image in images:
    print(image.get('src'))