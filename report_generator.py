import os
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Image, Spacer
from reportlab.lib.units import inch
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords', quiet=True)

# Use Path for better path handling
BASE_DIR = Path("/Users/nathankirchner/Workstuff/Projects/GWA_Reviewer/OUTPUT/IM_TEXT_DESCRIPTION")
BASE_DIR.mkdir(parents=True, exist_ok=True)

def read_text_file(filepath):
    """Read text file or create if doesn't exist"""
    try:
        # Try different encodings
        encodings = ['utf-8', 'ascii', 'iso-8859-1']
        for encoding in encodings:
            try:
                text = filepath.read_text(encoding=encoding)
                # Clean up the text while preserving intentional line breaks
                text = text.replace('\r\n', '\n')  # Normalize line endings
                text = text.replace('\r', '\n')    # Convert any remaining \r to \n
                text = '\n'.join(line for line in text.split('\n') if line.strip())  # Remove empty lines
                text = ''.join(char for char in text if ord(char) < 128)  # Remove non-ASCII chars
                return text.strip()
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail, use utf-8 with error handling
        return filepath.read_text(encoding='utf-8', errors='replace').strip()
        
    except FileNotFoundError:
        print(f"Creating placeholder text for: {filepath.name}")
        placeholder = f"Placeholder text for {filepath.name}"
        filepath.write_text(placeholder, encoding='utf-8')
        return placeholder

def create_wordcloud(text_descriptions):
    """Generate wordcloud from text"""
    # Remove <br/> tags before generating wordcloud
    cleaned_text = [text.replace('<br/>', ' ') for text in text_descriptions]
    
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        stopwords=set(stopwords.words('english')),
        max_words=100
    ).generate(' '.join(cleaned_text))
    
    img_buf = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(img_buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    return img_buf

def create_report():
    # Setup document
    output_file = BASE_DIR / f"Report_{datetime.now().strftime('%Y%m%d')}.pdf"
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        topMargin=inch,
        bottomMargin=inch,
        leftMargin=inch,
        rightMargin=inch
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20
    )
    normal_style = styles['Normal']

    # Content
    story = []
    
    # Cover page
    cover_image_path = BASE_DIR / "20250217 GWA Reviewer Report Cover.png"
    if cover_image_path.exists():
        # Create cover image with specific size for first page
        cover_img_first = Image(str(cover_image_path))
        cover_img_first.drawHeight = 9*inch  # Adjust these values as needed
        cover_img_first.drawWidth = 7*inch   # Adjust these values as needed
        story.append(cover_img_first)
        story.append(PageBreak())
    
    # First page
    story.append(Paragraph("Image Analysis Report // GWA Reviewer AI", title_style))
    story.append(Paragraph(read_text_file(BASE_DIR / "report preamble.txt"), normal_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(read_text_file(BASE_DIR / "executive summary.txt"), normal_style))
    story.append(Paragraph("Aggregated Summary", heading_style))
    story.append(Paragraph(read_text_file(BASE_DIR / "aggregated summary.txt"), normal_style))
    story.append(PageBreak())

    # Image analysis pages
    text_descriptions = []
    screenshots = [
        "1",
        "2"
    ]

    for screenshot in screenshots:
        img_path = BASE_DIR / f"{screenshot}.png"
        txt_path = BASE_DIR / f"{screenshot}.txt"
        
        if img_path.exists():
            story.append(Paragraph(screenshot, heading_style))
            img = Image(str(img_path))
            img.drawHeight = 4*inch
            img.drawWidth = 6*inch
            story.append(img)
            
            description = read_text_file(txt_path)
            text_descriptions.append(description)
            story.append(Spacer(1, 20))
            story.append(Paragraph(description, normal_style))
            story.append(PageBreak())
        else:
            print(f"Warning: Image not found: {img_path}")

    # Word cloud and insights
    if text_descriptions:
        story.append(Paragraph("Analysis Insights", heading_style))
        
        wordcloud_buf = create_wordcloud(text_descriptions)
        wordcloud_img = Image(wordcloud_buf)
        wordcloud_img.drawHeight = 4*inch
        wordcloud_img.drawWidth = 7*inch
        story.append(wordcloud_img)
        
        # Read insights from file
        story.append(Spacer(1, 20))
        story.append(Paragraph("Key Insights:", heading_style))
        insights = read_text_file(BASE_DIR / "report insights.txt")
        story.append(Paragraph(insights, normal_style))
        story.append(PageBreak())

    # Final page
    story.append(Paragraph("Conclusion", heading_style))
    story.append(Paragraph(read_text_file(BASE_DIR / "report conclusion.txt"), normal_style))

    # Final cover page
    if cover_image_path.exists():
        # Create a new image instance with specific size for last page
        cover_img_last = Image(str(cover_image_path))
        cover_img_last.drawHeight = 9*inch  # Adjust these values as needed
        cover_img_last.drawWidth = 7*inch   # Adjust these values as needed
        story.append(cover_img_last)

    # Generate PDF
    doc.build(story)
    print(f"Report generated successfully: {output_file}")

if __name__ == "__main__":
    create_report()
