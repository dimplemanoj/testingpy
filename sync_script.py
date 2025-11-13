import os
import requests
from bs4 import BeautifulSoup

# Get environment variables
CONFLUENCE_URL = os.environ['CONFLUENCE_URL']
EMAIL = os.environ['CONFLUENCE_EMAIL']
API_TOKEN = os.environ['CONFLUENCE_API_TOKEN']
PAGE_ID = os.environ['PAGE_ID']

# Fetch Confluence page
auth = (EMAIL, API_TOKEN)
response = requests.get(
    f"{CONFLUENCE_URL}/rest/api/content/{PAGE_ID}?expand=body.storage",
    auth=auth
)

data = response.json()
html_content = data['body']['storage']['value']

# Parse HTML and extract your specific section
soup = BeautifulSoup(html_content, 'html.parser')

# Example: Extract content under a specific heading
section_heading = soup.find('h2', string='Your Section Name')
if section_heading:
    # Get all content until next heading
    content = []
    for sibling in section_heading.find_next_siblings():
        if sibling.name in ['h1', 'h2', 'h3']:
            break
        content.append(sibling.get_text())
    
    # Write to file
    with open('abc.md', 'w') as f:
        f.write('\n'.join(content))
