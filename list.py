import re

def filter_pages_with_dates(pages_data):
    """
    Filters a list of page data and prints the page name if a date or update mention
    is found, including information hidden within {% hint style="info" %} blocks.
    """
    print("📋 Pages/Sections in the Repository with a Date Mention:")
    print("-" * 50)
    found_pages = 0

    # Pattern to look for common date/time/duration indicators
    date_patterns = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4}|days ago|releases|updated)"

    # Regex to extract content from hint blocks (non-greedy match)
    # It accounts for both {% endhint %} and {% endhint %} (with extra space)
    hint_pattern = r"{%\s*hint style=\"info\"\s*%}(.*?){%\s*endhint\s*%}"

    for page in pages_data:
        page_name = page['page_name']
        page_content = page['update_info'] # Now representing the full content chunk

        # 1. Search for dates in the main content chunk directly
        search_text = page_content

        # 2. Extract content from hint blocks and add it to the search text
        hint_matches = re.findall(hint_pattern, page_content, re.DOTALL)
        for match in hint_matches:
            # Append the extracted hint content to the main search text
            search_text += " " + match.strip()

        # 3. Check the consolidated search text for a date pattern
        if re.search(date_patterns, search_text, re.IGNORECASE):
            # To make the output clean, we'll try to show what date was found
            found_date = re.search(date_patterns, search_text, re.IGNORECASE).group(0)

            print(f"- **{page_name}** (Date/Update Found: '{found_date}')")
            found_pages += 1

    if found_pages == 0:
        print("No pages with clear date mentions were found in the provided data.")
    print("-" * 50)
