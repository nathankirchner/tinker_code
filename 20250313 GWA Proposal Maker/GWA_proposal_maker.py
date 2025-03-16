import os
import sys
from pathlib import Path
from fpdf import FPDF
import openai
from tkinter import filedialog, Tk
import re


# Debug flag - Set to True to use dummy text instead of OpenAI
USE_DUMMY_TEXT = False

class ProposalPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Set effective page area
        self.set_margins(left=20, top=50, right=20)  # Increased top margin for header
        self.set_auto_page_break(auto=True, margin=50)  # Increased bottom margin for footer
        self.last_page = False
        
    def header(self):
        if self.page_no() > 1 and not self.last_page:
            # Header area
            self.set_y(10)
            self.image(os.path.join('GWA_logo.png'), x=20, y=10, w=60)
            self.set_y(40)  # Move starting position for text
            self.set_draw_color(128, 128, 128)
            self.line(20, 33, 190, 33)
        
    def footer(self):
        if self.page_no() > 1 and not self.last_page:
            # Footer area starts 100mm from bottom
            footer_y = 297 - 50  # A4 height (297mm) minus footer botton
            self.set_y(footer_y)
            self.set_draw_color(128, 128, 128)
            self.line(20, footer_y, 190, footer_y)
            self.image(os.path.join('nk_QR_footer.png'), x=140, y=footer_y + 10, w=42)

    def chapter_title(self, title):
        # Helper function for consistent chapter titles
        self.set_y(50)  # Start below header
        self.set_fill_color(240, 240, 240)
        self.set_font('Helvetica', 'B', size=20)  # Keep chapter titles large
        self.set_text_color(70, 70, 70)
        self.cell(0, 15, title, align='L', fill=True)
        self.ln(25)

def check_required_files():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(script_dir, 'source')
    
    print(f"\n📂 Looking for files in source directory: {source_dir}")
    
    required_files = ['COMPANY.txt', 'GOAL.txt', 'SOW.txt', 'COSTS-TIMELINES.txt', 
                      'GWA_logo.png', 'nk_QR_footer.png', 'nk_QR_cover.png']
    missing_files = []
    
    # Check if source directory exists
    if not os.path.exists(source_dir):
        print("❌ Source directory not found!")
        print("Creating source directory...")
        os.makedirs(source_dir)
        missing_files = required_files  # All files will be missing
    else:
        # Check for each required file in the source directory
        for file in required_files:
            file_path = os.path.join(source_dir, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please select the folder containing the required files.")
        
        root = Tk()
        root.withdraw()  # Hide the main window
        
        folder_path = filedialog.askdirectory(title="Select folder with required files")
        
        if not folder_path:
            print("❌ No folder selected. Exiting...")
            sys.exit(1)
            
        # Copy missing files from selected folder to source directory
        print(f"📝 Copying missing files to source directory...")
        for file in missing_files:
            src_path = os.path.join(folder_path, file)
            dst_path = os.path.join(source_dir, file)
            if os.path.exists(src_path):
                import shutil
                shutil.copy2(src_path, dst_path)
                print(f"✅ Copied {file}")
            else:
                print(f"❌ Could not find {file} in selected folder")
        
        # Check again
        missing_files = [file for file in required_files if not os.path.exists(os.path.join(source_dir, file))]
        if missing_files:
            print(f"❌ Still missing required files: {', '.join(missing_files)}")
            print("Please ensure all required files are present. Exiting...")
            sys.exit(1)
    
    # Change working directory to source directory
    os.chdir(source_dir)
    print(f"✅ All required files found in source directory")

def get_context_urls():
    return [
        "https://www.greywalladvisory.com/gwa-what",
        "https://www.greywalladvisory.com/",
        "https://www.nathankirchner.com",
        "https://www.linkedin.com/in/nkirchner/"
    ]

def get_dummy_text(word_count=200):
    """Generate lorem ipsum text with approximately the requested word count"""
    lorem_ipsum = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
    Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.
    """
    # Clean up the text
    words = lorem_ipsum.replace('\n', ' ').split()
    # Repeat the text if needed to reach desired word count
    while len(words) < word_count:
        words.extend(words)
    return ' '.join(words[:word_count])

def sanitize_text(text):
    """Replace special characters with their simple equivalents"""
    replacements = {
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '–': '-',      # en dash
        '—': '-',      # em dash
        '\u2010': '-', # hyphen
        '\u2011': '-', # non-breaking hyphen
        '\u2012': '-', # figure dash
        '\u2013': '-', # en dash
        '\u2014': '-', # em dash
        '\u2015': '-', # horizontal bar
        '‐': '-',      # hyphen
        '‑': '-',      # non-breaking hyphen
        '−': '-',      # minus sign
        '⁃': '-',      # hyphen bullet
        '₋': '-',      # subscript minus
        '⁻': '-',      # superscript minus
        '—': '-',      # em dash
        '–': '-',      # en dash
        '…': '...',
        '•': '*',
        '\u2019': "'",  # Right single quotation mark
        '\u2018': "'",  # Left single quotation mark
        '\u201C': '"',  # Left double quotation mark
        '\u201D': '"',  # Right double quotation mark
        '\u2026': '...', # Ellipsis
        '\u20ac': 'EUR', # Euro symbol
        '€': 'EUR',      # Euro symbol (direct)
        '£': 'GBP',      # British Pound
        '¥': 'JPY',      # Yen
        '₹': 'INR',      # Indian Rupee
        '$': 'USD',      # Dollar
        '¢': 'c',        # Cents
        '±': '+/-',      # Plus-minus
        '©': '(c)',      # Copyright
        '®': '(R)',      # Registered trademark
        '™': '(TM)',     # Trademark
        '°': ' degrees', # Degree symbol
        '½': '1/2',      # Fractions
        '¼': '1/4',
        '¾': '3/4',
        '\n': ' ',       # Replace newlines with spaces
        '\r': ' ',       # Replace carriage returns with spaces
        '\t': ' '        # Replace tabs with spaces
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Clean up multiple spaces
    text = ' '.join(text.split())
    
    # Ensure all remaining hyphens are the standard ASCII hyphen
    text = re.sub(r'[‐‑−⁃₋⁻—–]', '-', text)
    
    return text

def format_sow_text(text):
    """Format SOW text to preserve phase numbers and add bullet points"""
    # Split text into paragraphs
    paragraphs = text.split('\n')
    formatted = []
    
    for para in paragraphs:
        # If it's a phase header (matches "Phase X:" pattern)
        if re.match(r'Phase \d+:', para.strip()):
            # Add extra space before phase (except first one)
            if formatted:
                formatted.append('')
            formatted.append(para.strip())
        else:
            # Add hyphens instead of bullet points for non-phase lines that aren't empty
            if para.strip():
                formatted.append('- ' + para.strip())
    
    return '\n'.join(formatted)

def generate_ai_content(prompt, max_words=200, is_sow=False):
    print(f"\n🤖 Generating content for: {prompt[:50]}...")
    
    if USE_DUMMY_TEXT:
        print("   Using dummy text (Lorem Ipsum)")
        content = get_dummy_text(max_words)
    else:
        try:
            print("   Making API call to OpenAI...")
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": (
                        "You are an AI assistant helping to write a business proposal. "
                        "Please use these URLs as reference material for accurate information about Grey Wall Advisory and Nathan Kirchner: "
                        f"{', '.join(get_context_urls())}"
                    )},
                    {"role": "user", "content": (
                        f"Generate approximately {max_words} words on the following topic: {prompt}\n"
                        "If this is a Statement of Work, use 'Phase X:' format for different phases and separate distinct activities with bullet points."
                        if is_sow else prompt
                    )}
                ]
            )
            print("   ✅ Successfully generated content")
            content = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"   ❌ Error generating AI content: {e}")
            content = f"Error generating content for: {prompt}"
    
    # Apply SOW formatting if needed
    if is_sow:
        content = format_sow_text(sanitize_text(content))
    else:
        content = sanitize_text(content)
    
    return content

def read_file_content(filename):
    try:
        with open(filename, 'r') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return ""

def sanitize_filename(filename):
    # Remove or replace invalid filename characters
    import re
    
    # Remove URL components more thoroughly
    sanitized = re.sub(r'https?:?/?/?', '', filename)  # Remove http://, https://, http:, https:
    sanitized = re.sub(r'www\.', '', sanitized)        # Remove www.
    sanitized = re.sub(r'[\\/*?:"<>|]', '', sanitized) # Remove invalid filename characters
    sanitized = sanitized.replace('/', '_').replace('\\', '_')
    sanitized = sanitized.strip('.')  # Remove leading/trailing periods
    sanitized = sanitized.strip()     # Remove leading/trailing whitespace
    
    # If empty after sanitization, use default name
    if not sanitized:
        sanitized = "Company"
    return sanitized

def create_proposal():
    print("\n📋 Starting proposal generation process...")
    check_required_files()
    
    # Initialize PDF
    pdf = ProposalPDF()
    
    # Cover Page (no header/footer)
    print("\n📝 Generating cover page...")
    pdf.add_page()
    pdf.image('GWA_logo.png', x=10, y=30, w=180)
    
    pdf.set_font('Helvetica', 'B', size=28)  # Keep main title large
    pdf.ln(50)
    pdf.set_text_color(70, 70, 70)
    pdf.cell(0, 10, 'Proposal for', align='C')
    pdf.ln(15)
    pdf.set_font('Helvetica', 'B', size=24)  # Keep subtitle large
    pdf.cell(0, 10, 'First Step Engagement', align='C')
    
    company_name = read_file_content('COMPANY.txt')
    pdf.ln(20)
    pdf.set_font('Helvetica', 'B', size=18)  # Keep company name prominent
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f'Prepared for {company_name}', align='C')
    
    pdf.ln(15)
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")
    pdf.set_font('Helvetica', '', size=10)  # Updated to 10
    pdf.cell(0, 10, current_date, align='C')
    pdf.image('nk_QR_cover.png', x=100, y=240, w=90)
    
    # Executive Summary Page
    print("\n📝 Generating executive summary...")
    pdf.add_page()
    pdf.chapter_title('Executive Summary')
    
    # Problem section
    pdf.set_font('Helvetica', 'B', size=14)  # Keep section headers visible
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'Industry Challenge', align='L')
    pdf.ln(10)
    pdf.set_font('Helvetica', '', size=10)  # Updated to 10
    pdf.set_text_color(70, 70, 70)
    problem_text = generate_ai_content('AEC is great but needs help (Problem)')
    pdf.multi_cell(0, 10, problem_text, align='J')
    pdf.ln(15)
    
    # Only add solution section if there's enough space
    if pdf.get_y() < 190:  # Check if we're not too close to footer
        pdf.set_font('Helvetica', 'B', size=14)  # Keep section headers visible
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, 'Our Solution', align='L')
        pdf.ln(10)
        pdf.set_font('Helvetica', '', size=10)  # Updated to 10
        pdf.set_text_color(70, 70, 70)
        solution_text = generate_ai_content("I can help with general getting investment ready, building out networks for success & Robotics +AI in construction automation of course! (Solution)")
        pdf.multi_cell(0, 10, solution_text, align='J')
    else:
        pdf.add_page()
        pdf.set_y(70)  # Start below header
        pdf.set_font('Helvetica', 'B', size=14)  # Keep section headers visible
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, 'Our Solution', align='L')
        pdf.ln(10)
        pdf.set_font('Helvetica', '', size=10)  # Updated to 10
        pdf.set_text_color(70, 70, 70)
        solution_text = generate_ai_content("I can help with general getting investment ready, building out networks for success & Robotics +AI in construction automation of course! (Solution)")
        pdf.multi_cell(0, 10, solution_text, align='J')

    # Continue with other sections, using chapter_title and checking space
    print("\n📝 Generating goals section...")
    pdf.add_page()
    pdf.chapter_title('Engagement Goals')
    goal_text = read_file_content('GOAL.txt')
    goal_prompt = f"Based on the goal: {goal_text}, explain how achieving these goals will benefit {company_name}"
    goal_elaboration = generate_ai_content(goal_prompt)
    pdf.set_font('Helvetica', '', size=10)  # Updated to 10
    pdf.multi_cell(0, 10, goal_elaboration, align='J')
    
    # Scope of Work
    print("\n📝 Generating scope of work...")
    pdf.add_page()
    pdf.chapter_title('Scope of Work')
    sow_text = read_file_content('SOW.txt')
    sow_elaboration = generate_ai_content(f"Elaborate on this Statement of Work: {sow_text}", is_sow=True)
    pdf.set_font('Helvetica', '', size=10)
    
    # Split SOW text and apply formatting
    for line in sow_elaboration.split('\n'):
        if re.match(r'Phase \d+:', line.strip()):
            # Phase headers in bold
            pdf.set_font('Helvetica', 'B', size=10)
            pdf.ln(5)
            pdf.multi_cell(0, 10, line.strip(), align='L')
            pdf.set_font('Helvetica', '', size=10)  # Reset to regular weight after phase header
            pdf.ln(2)
        elif line.strip():
            # Regular lines with proper indentation
            if line.startswith('-'):
                pdf.set_x(25)  # Indent list items
            pdf.multi_cell(0, 10, line.strip(), align='L')
    
    # Investment and Timeline
    print("\n📝 Generating investment and timeline...")
    pdf.add_page()
    pdf.chapter_title('Investment and Timeline')
    costs_timeline_text = read_file_content('COSTS-TIMELINES.txt')
    costs_elaboration = generate_ai_content(f"Elaborate on these costs and timelines: {costs_timeline_text}")
    pdf.set_font('Helvetica', '', size=10)  # Updated to 10
    pdf.multi_cell(0, 10, costs_elaboration, align='J')
    
    # Next Steps (Final Page)
    print("\n📝 Generating next steps...")
    pdf.add_page()
    pdf.set_y(70)  # Consistent with other pages
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Helvetica', 'B', size=20)
    pdf.cell(0, 15, 'Next Steps', align='L', fill=True)
    pdf.ln(25)
    
    conclusion_prompt = f"Write a conclusion about delivering the SOW ({sow_text}) and how it will help {company_name} achieve their goals ({goal_text})"
    conclusion_text = generate_ai_content(conclusion_prompt, 300)
    pdf.set_font('Helvetica', '', size=10)  # Updated to 10
    pdf.multi_cell(0, 10, conclusion_text, align='J')
    pdf.ln(20)
    
    # Contact section
    if pdf.get_y() < 180:  # Check if there's enough space for contact section
        pdf.set_fill_color(245, 245, 245)
        pdf.set_font('Helvetica', 'I', size=10)  # Updated to 10
        pdf.set_text_color(100, 100, 100)
        contact_text = generate_ai_content("Write a 50-word 'contact me and let's get started' message", 50)
        pdf.multi_cell(0, 10, contact_text, align='C', fill=True)
        pdf.ln(10)
        
        # Add specific contact information
        pdf.set_font('Helvetica', 'B', size=12)  # Keep contact header visible
        pdf.cell(0, 10, 'Contact Grey Wall Advisory', align='C')
        pdf.ln(8)
        pdf.set_font('Helvetica', '', size=10)  # Updated to 10
        pdf.cell(0, 10, 'nathankirchner@gmail.com', align='C')
        pdf.ln(8)
        pdf.cell(0, 10, '+61 403 845 487', align='C')
    
    # Save the PDF in script directory
    print("\n💾 Saving PDF...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    safe_company_name = sanitize_filename(company_name)
    output_filename = f"GWA_Proposal_{safe_company_name}.pdf"
    output_path = os.path.join(script_dir, output_filename)
    
    # Change back to script directory before saving
    original_dir = os.getcwd()  # Save current directory (source folder)
    os.chdir(script_dir)        # Change to script directory
    pdf.output(output_filename)  # Save PDF
    os.chdir(original_dir)      # Change back to source folder
    
    print(f"\n✨ Success! Proposal has been generated: {output_path}")

if __name__ == "__main__":
    if not os.getenv('OPENAI_API_KEY'):
        print("Please set your OPENAI_API_KEY environment variable")
        sys.exit(1)
    create_proposal()
