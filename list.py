import re
import os

# --- CONFIGURE THIS PATH ---
REPO_PATH = 'https://github.com/dimplemanoj/testingpy' 
# Example: 'C:/Users/YourName/Documents/testingpy' or '/Users/YourName/testingpy'

# ---------------------------

def filter_files_for_banners(repo_directory):
    """
    Scans files in the directory for date mentions, including those within hint blocks.
    """
    print("📋 Scanning Repository Files for Expiration Date Banners:")
    print("-" * 50)
    found_files = 0
    
    # Date patterns and the hint block pattern remain the same
    date_patterns = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4}|days ago|releases|updated|expire|expiry|expiration)"
    hint_pattern = r"{%\s*hint style=\"info\"\s*%}(.*?){%\s*endhint\s*%}"

    # Use os.listdir to get all file names in the directory
    for filename in os.listdir(repo_directory):
        file_path = os.path.join(repo_directory, filename)

        # Skip directories and non-text files (optional, but good practice)
        if os.path.isdir(file_path):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except Exception as e:
            # Skip files that can't be read (e.g., binaries, permission issues)
            print(f"Skipping {filename}: Could not read content. ({e})")
            continue

        # --- Logic to find dates/banners in the content ---
        search_text = file_content
        
        # Extract content from hint blocks and add it to the search text
        hint_matches = re.findall(hint_pattern, file_content, re.DOTALL)
        for match in hint_matches:
            search_text += " " + match.strip()

        # Check the consolidated text for a date pattern
        if re.search(date_patterns, search_text, re.IGNORECASE):
            found_date = re.search(date_patterns, search_text, re.IGNORECASE).group(0)

            print(f"- **{filename}** (Found Date/Keyword: '{found_date}')")
            found_files += 1

    if found_files == 0:
        print("No files with clear expiration dates or date mentions were found.")
    print("-" * 50)

# Run the function with the configured path
filter_files_for_banners(REPO_PATH)
