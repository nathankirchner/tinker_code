import os
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Image, Spacer, Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, NextPageTemplate
from reportlab.lib.units import inch
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords', quiet=True)

# Use Path for better path handling
BASE_DIR = Path(__file__).parent
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
    # Remove <br/> tags and 'image' word before generating wordcloud
    cleaned_text = [text.replace('<br/>', ' ').replace('image', '').replace('Image', '') for text in text_descriptions]
    
    # Add 'image' to stopwords
    custom_stopwords = set(stopwords.words('english'))
    custom_stopwords.update(['image', 'Image', 'camera', 'Camera'])
    
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        stopwords=custom_stopwords,
        max_words=100
    ).generate(' '.join(cleaned_text))
    
    img_buf = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(img_buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    return img_buf

class ReportTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        # Normal content frame
        frame = Frame(
            self.leftMargin,
            self.bottomMargin + 0.75*inch,  # Make room for footer
            self.width,
            self.height - 0.75*inch,
            id='normal'
        )
        # Footer frame
        footer_frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            0.75*inch,
            id='footer'
        )
        
        # First page template (no footer)
        first_template = PageTemplate(
            id='First',
            frames=frame,
            onPage=self.on_first_page
        )
        
        # Last page template (no footer)
        last_template = PageTemplate(
            id='Last',
            frames=frame,
            onPage=self.on_last_page
        )
        
        # Template for other pages (with footer)
        content_template = PageTemplate(
            id='Later',
            frames=frame,  # Only use main frame
            onPage=self.on_later_pages
        )
        
        self.addPageTemplates([first_template, content_template, last_template])
    
    def on_first_page(self, canvas, doc):
        pass
    
    def on_last_page(self, canvas, doc):
        pass
    
    def on_later_pages(self, canvas, doc):
        # Add logo to footer
        logo_path = BASE_DIR/ "IM_TEXT_DESCRIPTION" / "20250214 GWA Logo LONG WHITE LIGHT.png"
        if logo_path.exists():
            # Calculate position for center of page
            page_width = A4[0]
            logo_width = 1.3*inch
            logo_height = 0.4*inch
            x_position = 1*inch
            
            # Draw horizontal line at top of footer
            canvas.setStrokeColor(colors.HexColor('#CCCCCC'))
            canvas.line(
                inch,
                0.8*inch,
                page_width - inch,
                0.8*inch
            )
            
            # Draw logo
            canvas.drawImage(
                str(logo_path),
                x_position,
                0.25*inch,
                width=logo_width,
                height=logo_height
            )
            
            # Add URLs to center of footer
            canvas.setFont("Helvetica", 5)
            canvas.setFillColor(colors.HexColor('#AAAAAA'))
            
            # Calculate center position
            center_x = page_width / 2
            canvas.drawCentredString(
                center_x,
                0.45*inch,  # Top URL
                "https://greywalladvisory.com"
            )
            canvas.drawCentredString(
                center_x,
                0.35*inch,  # Bottom URL
                "https://www.linkedin.com/in/nkirchner/"
            )
            
            # Add text to right side of footer
            canvas.drawRightString(
                page_width - inch,
                0.4*inch,
                "202502 Kirchner"
            )

def create_report():
    # Setup document
    output_file = BASE_DIR / "OUTPUT" / f"Report_{datetime.now().strftime('%Y%m%d')}.pdf"
    doc = ReportTemplate(
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
    cover_image_path = BASE_DIR / "IM_TEXT_DESCRIPTION" / "20250217 GWA Reviewer Report Cover.png"
    if cover_image_path.exists():
        story.append(NextPageTemplate('Later'))
        # Calculate center position
        page_width = A4[0] - 2*inch  # Account for margins
        margin_space = (page_width - 5.8*inch) / 2
        story.append(Spacer(1, 0.5*inch))  # Top margin
        
        cover_img_first = Image(str(cover_image_path))
        cover_img_first.drawHeight = 8*inch
        cover_img_first.drawWidth = 5.8*inch
        cover_img_first.hAlign = 'CENTER'  # Center horizontally
        
        story.append(cover_img_first)
        story.append(PageBreak())
    
    # First page
    story.append(Paragraph("Image Analysis Report <br/><br/> GWA Reviewer AI", title_style))
    story.append(Paragraph(read_text_file(BASE_DIR / "IM_TEXT_DESCRIPTION" / "report preamble.txt"), normal_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(read_text_file(BASE_DIR / "IM_TEXT_DESCRIPTION" / "executive summary.txt"), normal_style))
    story.append(Paragraph("Aggregated Summary", heading_style))
    story.append(Paragraph(read_text_file(BASE_DIR / "IM_TEXT_DESCRIPTION" / "aggregated summary.txt"), normal_style))
    story.append(PageBreak())

    # Image analysis pages
    text_descriptions = []
    screenshots = [
        "1",
        "2"
    ]

    for screenshot in screenshots:
        img_path = BASE_DIR / "IM_TEXT_DESCRIPTION" / f"{screenshot}.png"
        txt_path = BASE_DIR / "IM_TEXT_DESCRIPTION" / f"{screenshot}.txt"
        
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
        story.append(Paragraph("Analysis Wordcloud", heading_style))
        
        wordcloud_buf = create_wordcloud(text_descriptions)
        wordcloud_img = Image(wordcloud_buf)
        wordcloud_img.drawHeight = 4*inch
        wordcloud_img.drawWidth = 7*inch
        story.append(wordcloud_img)
        
        # Read insights from file
        story.append(Spacer(1, 20))
        story.append(Paragraph("Key Insights:", heading_style))
        insights = read_text_file(BASE_DIR / "IM_TEXT_DESCRIPTION" / "report insights.txt")
        story.append(Paragraph(insights, normal_style))
        #story.append(PageBreak())

    # Final page
    story.append(Paragraph("Conclusion", heading_style))
    story.append(Paragraph(read_text_file(BASE_DIR / "IM_TEXT_DESCRIPTION" / "report conclusion.txt"), normal_style))

    # Before final cover page
    story.append(NextPageTemplate('Last'))  # Switch to last template before final cover
    
    # # Final cover page
    # if cover_image_path.exists():
    #     cover_img_last = Image(str(cover_image_path))
    #     cover_img_last.drawHeight = 8*inch  # Reduced from 9 to 8 inches
    #     cover_img_last.drawWidth = 6*inch   # Reduced from 7 to 6 inches
    #     story.append(cover_img_last)

    # Generate PDF
    doc.build(story)
    print(f"Report generated successfully: {output_file}")
    
    # Open the PDF
    import platform
    import subprocess
    
    if platform.system() == 'Darwin':       # macOS
        subprocess.run(['open', output_file])
    elif platform.system() == 'Windows':     # Windows
        subprocess.run(['start', output_file], shell=True)
    elif platform.system() == 'Linux':       # Linux
        subprocess.run(['xdg-open', output_file])

if __name__ == "__main__":
    create_report()
