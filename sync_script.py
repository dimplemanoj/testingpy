#!/usr/bin/env python3
import os
import requests
from bs4 import BeautifulSoup
import sys
import re

def html_table_to_markdown(table):
    """
    Convert HTML table to Markdown table format.
    """
    rows = table.find_all('tr')
    if not rows:
        return ""
    
    markdown_lines = []
    
    for i, row in enumerate(rows):
        # Get cells (th or td)
        cells = row.find_all(['th', 'td'])
        if not cells:
            continue
        
        # Extract text from each cell and clean it
        cell_texts = []
        for cell in cells:
            text = cell.get_text(separator=' ', strip=True)
            # Escape pipe characters in cell content
            text = text.replace('|', '\\|')
            # Replace newlines with space for markdown
            text = text.replace('\n', ' ')
            cell_texts.append(text)
        
        # Create markdown row
        markdown_row = '| ' + ' | '.join(cell_texts) + ' |'
        markdown_lines.append(markdown_row)
        
        # Add separator after header row (first row)
        if i == 0:
            separator = '| ' + ' | '.join(['---'] * len(cell_texts)) + ' |'
            markdown_lines.append(separator)
    
    return '\n'.join(markdown_lines)

def confluence_to_markdown(html_content):
    """
    Convert Confluence HTML to Markdown, including tables.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Process tables first - convert them to markdown
    tables = soup.find_all('table')
    for table in tables:
        markdown_table = html_table_to_markdown(table)
        # Replace the table with a placeholder
        placeholder = soup.new_tag('div', attrs={'class': 'markdown-table'})
        placeholder.string = f"\n{markdown_table}\n"
        table.replace_with(placeholder)
    
    # Now extract text with proper formatting
    result = []
    
    for element in soup.descendants:
        if element.name == 'h1':
            result.append(f"\n# {element.get_text(strip=True)}\n")
        elif element.name == 'h2':
            result.append(f"\n## {element.get_text(strip=True)}\n")
        elif element.name == 'h3':
            result.append(f"\n### {element.get_text(strip=True)}\n")
        elif element.name == 'h4':
            result.append(f"\n#### {element.get_text(strip=True)}\n")
        elif element.name == 'h5':
            result.append(f"\n##### {element.get_text(strip=True)}\n")
        elif element.name == 'h6':
            result.append(f"\n###### {element.get_text(strip=True)}\n")
        elif element.name == 'p':
            text = element.get_text(strip=True)
            if text:
                result.append(f"{text}\n")
        elif element.name == 'div' and 'markdown-table' in element.get('class', []):
            result.append(element.get_text())
        elif element.name == 'ul':
            for li in element.find_all('li', recursive=False):
                result.append(f"- {li.get_text(strip=True)}\n")
        elif element.name == 'ol':
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                result.append(f"{i}. {li.get_text(strip=True)}\n")
        elif element.name == 'code':
            if element.parent.name != 'pre':
                result.append(f"`{element.get_text(strip=True)}`")
        elif element.name == 'pre':
            code = element.find('code')
            if code:
                result.append(f"\n```\n{code.get_text()}\n```\n")
            else:
                result.append(f"\n```\n{element.get_text()}\n```\n")
        elif element.name == 'br':
            result.append('\n')
    
    # Join and clean up the result
    markdown = ''.join(result)
    
    # Clean up multiple newlines
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    
    return markdown.strip()

def extract_section_content(html_content, section_name=None):
    """
    Extract content from Confluence HTML and convert to Markdown.
    If section_name is provided, extracts content under that heading.
    Otherwise, extracts all content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    if section_name:
        # Find specific section by heading
        section_heading = soup.find(['h1', 'h2', 'h3', 'h4'], 
                                    string=lambda text: text and section_name.lower() in text.lower())
        
        if not section_heading:
            print(f"Warning: Section '{section_name}' not found, extracting all content")
            return confluence_to_markdown(str(soup))
        
        # Get heading level
        heading_level = section_heading.name
        
        # Create a new soup with just the section content
        section_html = [str(section_heading)]
        
        for sibling in section_heading.find_next_siblings():
            # Stop at next heading of same or higher level
            if sibling.name and sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if sibling.name <= heading_level:
                    break
            section_html.append(str(sibling))
        
        section_content = ''.join(section_html)
        return confluence_to_markdown(section_content)
    else:
        # Extract all content
        return confluence_to_markdown(html_content)

def main():
    # Get configuration from environment variables
    confluence_url = os.environ.get('CONFLUENCE_URL')
    email = os.environ.get('CONFLUENCE_EMAIL')
    api_token = os.environ.get('CONFLUENCE_API_TOKEN')
    page_id = os.environ.get('PAGE_ID')
    section_name = os.environ.get('SECTION_NAME', '')
    output_file = os.environ.get('OUTPUT_FILE', 'abc.md')
    
    # Debug: Print what we received (masking sensitive data)
    print("Configuration check:")
    print(f"  CONFLUENCE_URL: {'✓ Set' if confluence_url else '✗ Missing'}")
    print(f"  CONFLUENCE_EMAIL: {'✓ Set' if email else '✗ Missing'}")
    print(f"  CONFLUENCE_API_TOKEN: {'✓ Set' if api_token else '✗ Missing'}")
    print(f"  PAGE_ID: {page_id if page_id else '✗ Missing'}")
    print(f"  OUTPUT_FILE: {output_file}")
    if section_name:
        print(f"  SECTION_NAME: {section_name}")
    
    # Validate required variables
    if not confluence_url:
        print("\nError: CONFLUENCE_URL is not set")
        print("Example: https://your-company.atlassian.net/wiki")
        sys.exit(1)
    
    if not email:
        print("\nError: CONFLUENCE_EMAIL is not set")
        sys.exit(1)
    
    if not api_token:
        print("\nError: CONFLUENCE_API_TOKEN is not set")
        sys.exit(1)
    
    if not page_id:
        print("\nError: PAGE_ID is not set")
        sys.exit(1)
    
    # Remove trailing slash from URL if present
    confluence_url = confluence_url.rstrip('/')
    
    # Construct full URL
    api_url = f"{confluence_url}/rest/api/content/{page_id}"
    print(f"\nFetching from: {api_url}")
    
    try:
        # Fetch Confluence page content
        response = requests.get(
            api_url,
            params={'expand': 'body.storage'},
            auth=(email, api_token),
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 401:
            print("\nAuthentication failed. Please check:")
            print("  1. CONFLUENCE_EMAIL is correct")
            print("  2. CONFLUENCE_API_TOKEN is valid")
            print("  3. Token has not expired")
            sys.exit(1)
        
        if response.status_code == 404:
            print(f"\nPage not found. Please check:")
            print(f"  1. PAGE_ID ({page_id}) is correct")
            print(f"  2. Page exists and you have permission to view it")
            sys.exit(1)
        
        response.raise_for_status()
        
        data = response.json()
        html_content = data['body']['storage']['value']
        
        print(f"Successfully fetched page: {data.get('title', 'Unknown')}")
        
        # Count tables
        soup = BeautifulSoup(html_content, 'html.parser')
        table_count = len(soup.find_all('table'))
        if table_count > 0:
            print(f"Found {table_count} table(s) - will convert to Markdown")
        
        # Extract and convert content
        if section_name:
            print(f"Extracting section: {section_name}")
            content = extract_section_content(html_content, section_name)
        else:
            print("Extracting all content")
            content = extract_section_content(html_content)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content.strip() + '\n')
        
        print(f"Successfully updated {output_file}")
        print(f"Content length: {len(content)} characters")
        
    except requests.exceptions.RequestException as e:
        print(f"\nError fetching from Confluence: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
