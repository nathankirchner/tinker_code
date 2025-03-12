import os
from pathlib import Path
import csv
import time
from openai import OpenAI
import docx
import re
from urllib.parse import urlparse
import tkinter as tk
from tkinter import filedialog

# Debug flags
VERBOSE = True  # Set to True to see detailed debug output
PROGRESS = True  # Set to True to see basic progress (default)
TEST_MODE = "QUICK"  # Options: "QUICK" (1 URL), "NORMAL" (3 URLs), False (all URLs)

def debug_print(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)

def progress_print(*args, **kwargs):
    if PROGRESS:
        print(*args, **kwargs)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def extract_urls_from_rtf(file_path):
    """Extract URLs from RTF file"""
    try:
        debug_print(f"Opening file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            rtf_text = file.read()
            debug_print(f"File content length: {len(rtf_text)}")
            
            # Extract URLs from RTF hyperlink fields
            url_pattern = r'\\field.*?HYPERLINK "(.*?)"'
            urls = re.findall(url_pattern, rtf_text)
            debug_print(f"Found URLs: {urls}")
            
            # Filter out any non-URLs and clean them
            valid_urls = [url for url in urls if url.startswith('http')]
            debug_print(f"Valid URLs: {valid_urls}")
            
            return valid_urls
    except Exception as e:
        print(f"Error reading RTF file: {e}")  # Keep error messages visible
        return []

def clean_url(url):
    """Clean and standardize URL format."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def analyze_website(url):
    """Analyze website using ChatGPT to extract required information."""
    progress_print(f"\nAnalyzing URL: {url}")
    
    prompt = f"""
    Analyze the company at {url} and provide information in EXACTLY this format:
    company_name|description|aec_benefits|maturity

    Requirements:
    1. Use ONLY the pipe character (|) as separator
    2. Do NOT add any extra text or explanations
    3. Do NOT add line breaks within sections
    4. Ensure all 4 sections are present
    5. Do not include sources or inline citations
    
    Example format:
    CompanyXYZ|This company provides software for construction management...|Their solution benefits the AEC sector by...|Emerging

    Required sections:
    1. company_name: Just the company name
    2. description: 200-word description of their solution that makes sure to describe what their main product actually does & answers the question of 'what do they do?'. THis should be available in the text on their main page and / or on their 'about' page
    3. aec_benefits: 200-word description of AEC sector benefits
    4. maturity: ONLY use Early, Emerging, or Established

    Respond with ONLY the formatted response, no other text.
    """

    try:
        ##
        # THE RESULTS HERE ARE NOT THE SAME AS WHEN I PUT THE SAME PROMPT INTO THE CHATGP4 WEB INTERFACE USING THE SAME MODEL
        ##
        progress_print("Sending request to OpenAI...")
        response = client.chat.completions.create(
            model="gpt-4o-mini", # THE RESULTS HERE ARE NOT THE SAME AS WHEN I PUT THE SAME PROMPT INTO THE CHATGP4 WEB INTERFACE USING THE SAME MODEL
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Reduced temperature for more consistent formatting
            max_tokens=1000
        )
        
        # Parse the response
        content = response.choices[0].message.content.strip()
        progress_print(f"Raw response: {content}")
        
        result = content.split('|')
        progress_print(f"Split result length: {len(result)}")
        progress_print(f"Split result: {result}")
        
        if len(result) == 4:
            return result
        else:
            progress_print(f"❌ Error: Expected 4 parts but got {len(result)}")
            return None
            
    except Exception as e:
        progress_print(f"❌ Error analyzing {url}: {str(e)}")
        return None

def main():
    # Setup paths
    base_dir = Path(__file__).parent
    output_file = base_dir / "aec_companies.csv"
    default_rtf = base_dir / "20250310_AEC_Startups_to_add_to_DB.rtf"
    
    # Check for default RTF file first
    progress_print(f"\nLooking for default RTF file at:")
    progress_print(f"{default_rtf}")
    
    if default_rtf.exists():
        input_file = str(default_rtf)
        progress_print("✓ Found default RTF file!")
    else:
        progress_print("✗ Default RTF file not found")
        progress_print("\nPlease select the RTF file location manually...")
        
        # Create root window and hide it
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Open file dialog for selecting the RTF document
        input_file = filedialog.askopenfilename(
            title="Select RTF Document",
            filetypes=[("Rich Text Format", "*.rtf"), ("Word Document", "*.docx"), ("All files", "*.*")],
            initialdir=base_dir  # Start in the script directory
        )
    
    if not input_file:
        print("No file selected. Exiting...")
        return
    
    # Extract URLs
    progress_print(f"\nReading URLs from: {Path(input_file).name}")
    urls = extract_urls_from_rtf(input_file)
    debug_print(f"Extracted URLs: {urls}")
    
    if not urls:
        print("No URLs found in the file!")
        return
    
    # Limit URLs based on test mode
    if TEST_MODE == "QUICK":
        urls = urls[:1]
        progress_print("QUICK TEST MODE: Processing only first URL")
    elif TEST_MODE == "NORMAL":
        urls = urls[:3]
        progress_print("TEST MODE: Processing only first 3 URLs")
    
    progress_print(f"Found {len(urls)} URLs to process")
    
    # Prepare CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Company Name', 'URL', '', 'Solution Description', 
                        'AEC Benefits', 'Tags', 'Maturity', ''])
        
        # Process each URL
        for i, url in enumerate(urls, 1):
            progress_print(f"\nProcessing URL {i}/{len(urls)}: {urlparse(url).netloc}")
            clean_url_str = clean_url(url)
            progress_print(f"Cleaned URL: {clean_url_str}")
            
            # Analyze website
            result = analyze_website(clean_url_str)
            
            if result:
                try:
                    company_name, description, aec_benefits, maturity = result
                    writer.writerow([
                        company_name,
                        clean_url_str,
                        '',
                        description,
                        aec_benefits,
                        '',
                        maturity,
                        ''
                    ])
                    progress_print(f"✓ Successfully processed {company_name}")
                except Exception as e:
                    progress_print(f"❌ Error writing to CSV: {str(e)}")
            else:
                progress_print(f"❌ Failed to process {url}")
            
            # Add delay to respect API rate limits
            time.sleep(1)
            
    progress_print(f"\nProcessing complete. Results saved to: {output_file}")

if __name__ == "__main__":
    main() 