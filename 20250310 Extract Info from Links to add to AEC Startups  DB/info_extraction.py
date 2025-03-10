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

# Initialize OpenAI client
client = OpenAI(api_key='your-api-key-here')

def extract_urls_from_rtf(file_path):
    """Extract URLs from RTF file"""
    import striprtf.striprtf
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            rtf_text = file.read()
            # Convert RTF to plain text
            plain_text = striprtf.striprtf.rtf_to_text(rtf_text)
            
            # Use regex to find URLs
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, plain_text)
            
            return urls
    except Exception as e:
        print(f"Error reading RTF file: {e}")
        return []

def clean_url(url):
    """Clean and standardize URL format."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def analyze_website(url):
    """Analyze website using ChatGPT to extract required information."""
    prompt = f"""
    Analyze the company at {url} and provide the following information in a structured format:
    1. Company name
    2. A 200-word description of what their solution does
    3. A 200-word description of how it benefits the AEC (Architecture Engineering Construction) sector
    4. Relevant tags from the following list (only include applicable tags):
       Situational Awareness, Admin Productivity, Physical Productivity, Admin Process Improvement,
       Physical Process Improvement, Sensing & Perception, AI, Robotics Vision, RPA, Safety,
       Autonomous Earthworks, Autonomous Drilling, Contracting, Procurement, Estimating,
       Scheduling, Prequalification, Bid Management
    5. Maturity level (choose one): Early, Emerging, or Established
    
    Format the response as: company_name|description|aec_benefits|tags|maturity
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse the response
        result = response.choices[0].message.content.strip().split('|')
        if len(result) == 5:
            return result
        else:
            return None
            
    except Exception as e:
        print(f"Error analyzing {url}: {str(e)}")
        return None

def main():
    # Setup paths
    base_dir = Path(__file__).parent
    output_file = base_dir / "aec_companies.csv"
    
    # Create root window and hide it
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    # Open file dialog for selecting the RTF document
    input_file = filedialog.askopenfilename(
        title="Select RTF Document",
        filetypes=[("Rich Text Format", "*.rtf"), ("Word Document", "*.docx"), ("All files", "*.*")]
    )
    
    if not input_file:
        print("No file selected. Exiting...")
        return
    
    # Extract URLs
    urls = extract_urls_from_rtf(input_file)
    
    # Prepare CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Company Name', 'URL', '', 'Solution Description', 
                        'AEC Benefits', 'Tags', 'Maturity', ''])
        
        # Process each URL
        for url in urls:
            print(f"Processing {url}...")
            clean_url_str = clean_url(url)
            
            # Analyze website
            result = analyze_website(clean_url_str)
            
            if result:
                company_name, description, aec_benefits, tags, maturity = result
                writer.writerow([
                    company_name,
                    clean_url_str,
                    '',  # empty column
                    description,
                    aec_benefits,
                    tags,
                    maturity,
                    ''   # empty column
                ])
                
            # Add delay to respect API rate limits
            time.sleep(1)
            
    print(f"Processing complete. Results saved to {output_file}")

if __name__ == "__main__":
    main() 