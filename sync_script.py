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
    for table in tabl
